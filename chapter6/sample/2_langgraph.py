from langchain_core.messages import AIMessage
from langchain.chat_models import init_chat_model
from langgraph.types import Command
from langgraph.graph import StateGraph, MessagesState, START, END

# モデルを設定
model = init_chat_model(
    model="us.anthropic.claude-sonnet-4-20250514-v1:0",
    model_provider="bedrock_converse"
)

# エージェント作成関数（サイコロを振って行き先を決定）
def create_agent(name, odd_target, even_target):
    def agent(state):
        dice = int(str(model.invoke("1から6のサイコロを1つ振って、数字だけ答えて").content).strip())
        is_odd = dice % 2 == 1
        next_agent = odd_target if is_odd else even_target
        content = f"{name}: {dice}が出たので{next_agent}へ進みます！"
        print(content)
        return Command(goto=next_agent, update={"messages": [AIMessage(content=content)]})
    return agent

# 各エージェントを作成
agent_1 = create_agent("エージェント1", "agent_3", "agent_2")
agent_2 = create_agent("エージェント2", "agent_3", END)
agent_3 = create_agent("エージェント3", END, "agent_2")

# グラフを構築
builder = StateGraph(MessagesState)
builder.add_node("agent_1", agent_1)
builder.add_node("agent_2", agent_2)
builder.add_node("agent_3", agent_3)
builder.add_edge(START, "agent_1")
network = builder.compile()

# ネットワークを起動
network.invoke({"messages": []})