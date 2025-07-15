from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_aws import ChatBedrockConverse
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.types import Command

load_dotenv()

model = ChatBedrockConverse(
    model="us.anthropic.claude-sonnet-4-20250514-v1:0"
)

# エージェント作成関数
def create_agent(content: str, next_agent: str):
    def agent(state: MessagesState):
        new_message = HumanMessage(content=content)
        response = model.invoke(state["messages"] + [new_message])
        return Command(
            goto=next_agent,
            update={"messages": [new_message, response]},
        )
    return agent

# エージェントを作成
agent_1 = create_agent("十円もらいました", "agent_2")
agent_2 = create_agent("百円もらいました", "agent_3")
agent_3 = create_agent("いま合計いくら？", END)

# グラフを作成
builder = StateGraph(MessagesState)
builder.add_node("agent_1", agent_1)
builder.add_node("agent_2", agent_2)
builder.add_node("agent_3", agent_3)
builder.add_edge(START, "agent_1")

# グラフをコンパイルして実行
network = builder.compile()
result = network.invoke({"messages": []})
print(result)