import asyncio
import boto3
import operator
import os

from langchain.chat_models import init_chat_model
from langchain_core.messages import AnyMessage, AIMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel
from typing import Annotated, Dict, List, Union

from dotenv import load_dotenv
load_dotenv()

web_search = TavilySearch(max_results=2)

@tool
def send_aws_sns(text: str):
    """テキストをAWS SNSのトピックにPublishするツール"""
    topic_arn = os.getenv("SNS_TOPIC_ARN")
    sns_client = boto3.client('sns')
    sns_client.publish(TopicArn=topic_arn, Message=text)

tools = [web_search, send_aws_sns]

# LLMの初期化
llm_with_tools = init_chat_model(
    model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    model_provider="bedrock_converse",
).bind_tools(tools)

# ステートの定義
class AgentState(BaseModel):
    messages: Annotated[list[AnyMessage], operator.add]

builder = StateGraph(AgentState)

system_prompt = """
あなたの責務はユーザからの質問を調査し、結果を要約してAWS SNSに送ることです。
質問以外は全て「回答できない」とだけユーザに返してください。
検索は1回のみとしてください。
"""    
async def agent(state: AgentState) -> Dict[str, List[AIMessage]]:

    response = await llm_with_tools.ainvoke(
       [SystemMessage(system_prompt)] + state.messages
    )

    return {"messages": [response]}

builder.add_node("agent", agent)
builder.add_node("tools", ToolNode(tools))

# ルーティング関数：ツールノードかENDノードへ遷移する
def route_node(state: AgentState) -> Union[str]:
    last_message = state.messages[-1]  
    if not isinstance(last_message, AIMessage):
        raise ValueError("「AIMessage」以外のメッセージです。遷移が不正な可能性があります。")
    if not last_message.tool_calls:
        return END # ENDノードへ遷移
    return "tools" # ツールノードへ遷移

builder.add_edge(START, "agent")
builder.add_conditional_edges(
    "agent",
    route_node,
)
builder.add_edge("tools", "agent")

graph = builder.compile()

async def main():
    question = "生成AIについて教えて！！"
    response = await graph.ainvoke(
        {"messages":
            [
                HumanMessage(question)
            ]
        }
    )
    return response

response = asyncio.run(main())
print(response)