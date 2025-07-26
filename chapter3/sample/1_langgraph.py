from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, END

# モデルを定義
model = init_chat_model(
    model="us.anthropic.claude-sonnet-4-20250514-v1:0",
    model_provider="bedrock_converse"
)

# ノードを定義
def research(s: dict) -> dict:
    response = model.invoke(
        f"{s['topic']}について解説して"
    ).content
    return {"response": response}

# グラフを定義
g = StateGraph(dict)
g.add_node("research", research)
g.set_entry_point("research")
g.add_edge("research", END)

# グラフをコンパイルして実行
output = g.compile().invoke({"topic": "AIエージェント"})
print(output["response"])