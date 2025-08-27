import boto3
from typing import Literal
from langchain.tools.retriever import create_retriever_tool
from langchain.chat_models import init_chat_model
from langchain.embeddings import init_embeddings
from langchain_chroma import Chroma
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.types import Command
from langfuse.langchain import CallbackHandler

from dotenv import load_dotenv
load_dotenv()

# Embeddingインスタンスの生成
embedding = init_embeddings(
    model="amazon.titan-embed-text-v2:0",
    provider="bedrock",
)

# Chromaベクトルデータベースの読み出し
vector_store = Chroma(
    collection_name="service_information",
    embedding_function=embedding,
    persist_directory="./db/chroma_langchain_db",
)
# ベクトルデータベースのツール化
retriever_tool = create_retriever_tool(
    vector_store.as_retriever(search_kwargs={"k": 1}),
    "retriever_service_info",
    "Retrieve service information.",
)

# ファイル書き込みツールの定義
@tool
def create_report(report_text: str):
    """Output generated text to file"""
    with open("./report.txt", mode="w", encoding="utf-8") as f:
        f.write(report_text)

# ツールノードの定義
tools = [retriever_tool, create_report]
tool_node = ToolNode(tools)

# LLMインスタンスの生成
llm_with_tools = init_chat_model(
    model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    model_provider="bedrock_converse"
).bind_tools(tools)

# Bedrock Guardrailsを用いたNGワードの判定
bedrock_runtime_client = boto3.client("bedrock-runtime")
def check_tool_use(state: MessagesState) -> Command[Literal["tools"]]:
    tool_call = state["messages"][-1].tool_calls[0]

    if tool_call["name"] == "create_report":
        report_text = tool_call["args"]["report_text"]

        response = bedrock_runtime_client.apply_guardrail(
            guardrailIdentifier="xxxxxxxxxxxx", # ガードレールのID
            guardrailVersion="DRAFT",
            source="OUTPUT",
            content=[
                {
                    "text": {
                        "text": report_text,
                    },
                },
            ],
            outputScope="FULL"
        )
        if response["action"] == "GUARDRAIL_INTERVENED":
            # NGワードが見つかり、出力をブロックするとき
            # Commandクラスにより、ツールノードに遷移せず、agentノードに処理を戻す
            return Command(goto="agent", update={"messages": [ToolMessage(tool_call_id=tool_call["id"], content="許可されない用語が含まれています。回答出来ないとユーザに通知して終了します。")]})
        else:
            # NGワードが見つからなかったとき
            # Commandクラスを使って、ツールノードに遷移する
            return Command(goto="tools")
    # 利用ツールが"create_report"出ない場合は、そのままツールノードに遷移する
    return Command(goto="tools")
    

def call_model(state: MessagesState) -> Command[Literal["check_tool_use"]] :
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)

    if response.tool_calls:
        # ツール利用要求がある場合、check_tool_useノードに遷移する
        return Command(goto="check_tool_use", update={"messages": [response]}) 
    # ツール利用要求がない場合、ENDノードに遷移する
    return Command(goto=END, update={"messages": [response]}) 


workflow = StateGraph(MessagesState)
# ノードの定義
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)
workflow.add_node("check_tool_use", check_tool_use)
# エッジの定義
workflow.add_edge(START, "agent")
workflow.add_edge("tools", "agent")
# グラフのコンパイル
app = workflow.compile()

# AIエージェントの実行
messages = app.invoke(
    {
        "messages":[
            ("human", "オンライン学習サービスに関する情報を取得したデータそのままでファイル保存してください。結果はファイル保存のみしてください。")
        # ("human", "電子契約サービスに関する情報を取得したデータそのままでファイル保存してください。結果はファイル保存のみしてください。")
        ]
    },
    config={"callbacks": [CallbackHandler()]}
)
messages["messages"][-1].pretty_print()
