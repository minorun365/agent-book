import operator
from pydantic import BaseModel
from typing import Annotated, Literal, Dict, Any
from langgraph.graph import StateGraph, START, END

# ステートの定義
class State(BaseModel):
    id: int
    messages: Annotated[list[str], operator.add]

builder = StateGraph(State)

# ノード関数の定義
def search_web(state: State) -> Dict[str, Any]:
    return {"messages": ["WebSearch"]}

def summarize(state: State) -> Dict[str, Any]:
    return {"messages": ["Summarizer"]}

def save_record(state: State) -> Dict[str, Any]:
    return {"messages": ["Recorder"]}

# ルーティング関数の定義
def routing_function(state: State) -> Literal["Summarizer", "Recorder"]:
    if state.id == 123:
        return "Summarizer"  # Summarizerに遷移する
    else:
        return "Recorder"  # Recorderに遷移する

# ノードの定義
builder.add_node("WebSearch", search_web)
builder.add_node("Summarizer", summarize)
builder.add_node("Recorder", save_record)

# エッジの定義
builder.add_edge(START, "WebSearch")
builder.add_conditional_edges("WebSearch", routing_function)
builder.add_edge("Summarizer", END)
builder.add_edge("Recorder", END)

# グラフのコンパイル
graph = builder.compile()

# グラフの同期実行
response = graph.invoke({"id": 123, "messages": ["start"]})
print(response)