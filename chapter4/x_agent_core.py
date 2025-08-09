from botocore.config import Config
from langchain.chat_models import init_chat_model
from langchain_community.agent_toolkits import FileManagementToolkit
from langchain_tavily import TavilySearch
from langchain_core.messages import (
    BaseMessage, 
    SystemMessage, 
    AIMessage, 
    ToolMessage, 
    ToolCall
)
from langgraph.types import interrupt
from langgraph.checkpoint.memory import MemorySaver
from langgraph.func import entrypoint, task
from langgraph.graph import add_messages

# .envから環境変数ファイルを読みだし
from dotenv import load_dotenv
load_dotenv(override=True)

# ツールの定義
# Web検索ツール
web_search = TavilySearch(max_results=2, topic="general")

working_directory = "report"
file_toolkit = FileManagementToolkit(
    root_dir=str(working_directory),
    selected_tools=["write_file"], # ファイル書き込みツールを指定
)
write_file = file_toolkit.get_tools()[0]

# 使用するツールのリスト
tools = [web_search, write_file]
tools_by_name = {tool.name: tool for tool in tools}

# LLMの初期化
cfg = Config(
    read_timeout=300,
)
llm_with_tools = init_chat_model(
    model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    model_provider="bedrock_converse",
    config=cfg,
).bind_tools(tools)

# システムプロンプト
system_prompt = """
あなたの責務はユーザからのリクエストを調査し、調査結果をファイル出力することです。
- ユーザのリクエスト調査にWeb検索が必要であれば、Web検索ツールを使ってください。
- 必要な情報が集まったと判断したら検索は終了して下さい。
- 検索は最大2回までとしてください。
- ファイル出力はHTML形式(.html)に変換して保存してください。
  * Web検索が拒否された場合、Web検索を中止してください。
  * レポート保存を拒否された場合、レポート作成を中止して、内容をユーザに直接伝えて下さい。
"""

# LLMを呼び出すタスク
@task
def invoke_llm(messages: list[BaseMessage]) -> AIMessage:
    response = llm_with_tools.invoke(
       [SystemMessage(content=system_prompt)] + messages
    )
    return response

# ツールを実行するタスク
@task
def use_tool(tool_call):
    tool = tools_by_name[tool_call["name"]]
    observation = tool.invoke(tool_call["args"])
    
    return ToolMessage(content=observation, tool_call_id=tool_call["id"])

# ユーザーにツール実行承認を求める
def ask_human(tool_call: ToolCall):
    tool_data = {"name": tool_call["name"]}
    if tool_call["name"] == web_search.name:
        args = f'* ツール名\n  * {tool_call["name"]}\n'
        args += "* 引数\n"
        for key, value in tool_call["args"].items():
          args += f"  * {key}\n    * {value}\n"

        tool_data["args"] = args
    elif tool_call["name"] == write_file.name:
        args = f'* ツール名\n  * {tool_call["name"]}\n'
        args += f'* 保存ファイル名\n  * {tool_call["args"]["file_path"]}'
        tool_data["html"] = tool_call["args"]["text"]
    tool_data["args"] = args

    feedback = interrupt(tool_data)

    if feedback == "APPROVE": # ユーザがツール利用を承認したとき
        return tool_call
    
    # ユーザがツール利用を承認しなかったとき
    return ToolMessage(
        content="ユーザによってツール利用が拒否されました。そのため処理を終了してください。", 
        name=tool_call["name"], 
        tool_call_id=tool_call["id"]
    )
    
# チェックポインターの設定
checkpointer = MemorySaver()
@entrypoint(checkpointer)
def agent(messages):
    # LLMを呼び出し
    llm_response = invoke_llm(messages).result()
    
    # ツール呼び出しがある限り繰り返す
    while True:
        if not llm_response.tool_calls:
            break

        approve_tools = []
        tool_results = []
        
        # 各ツール呼び出しに対してユーザーの承認を求める
        for tool_call in llm_response.tool_calls:
            feedback = ask_human(tool_call)
            if isinstance(feedback, ToolMessage):
                tool_results.append(feedback)
            else:
                approve_tools.append(feedback)

        # 承認されたツールを実行
        tool_futures = []
        for tool_call in approve_tools:
            future = use_tool(tool_call)   # 非同期実行を開始
            tool_futures.append(future)     # 後でまとめて結果を取り出すために保存

        # Future が完了するのを待って結果だけを集める
        tool_use_results = []
        for future in tool_futures:
            result = future.result()       # 完了まで待ち、結果を取得
            tool_use_results.append(result)

        # メッセージリストに追加
        messages = add_messages(messages, [llm_response, *tool_use_results, *tool_results])

        # モデルを再度呼び出し
        llm_response = invoke_llm(messages).result()
    
    # 最終結果を返す
    return llm_response