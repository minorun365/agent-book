from langchain.chat_models import init_chat_model
from langchain_community.agent_toolkits import FileManagementToolkit
from langchain_tavily import TavilySearch
from langfuse.langchain import CallbackHandler
from langgraph.prebuilt import create_react_agent

# 環境変数の読み込み
from dotenv import load_dotenv
load_dotenv()

# Web検索ツールの初期化
# Tavily検索エンジンを使用してWeb検索機能を提供
web_search = TavilySearch(max_results=2, topic="general")

# ファイル管理ツールキットの初期化
# 指定されたディレクトリ内でファイルの読み書きを行うツールを提供
file_toolkit = FileManagementToolkit(
    root_dir="report",
    selected_tools=["read_file", "write_file"],
)

# LLMインスタンスの生成
llm = init_chat_model(
    model="us.anthropic.claude-sonnet-4-20250514-v1:0",
    model_provider="bedrock_converse"
)
# AIエージェントの構築
agent = create_react_agent(llm, file_toolkit.get_tools() + [web_search])

# エージェントへのクエリ設定
# task.txtファイルを読み込んで、その内容に基づいてタスクを実行するよう指示
query = {
    "messages": [
        ("human", "task.txtを読み込んで依頼を解決してください。")
    ]
}
# Langfuseトレーシング設定
config = {"callbacks": [CallbackHandler()]}
# エージェントの実行
response = agent.invoke(query, config=config)

# 実行結果の表示
if 'messages' in response and response['messages']:
    last_message = response['messages'][-1]
    # メッセージオブジェクトの内容を適切に表示
    if hasattr(last_message, 'content'):
        print(last_message.content)
    else:
        print(last_message)