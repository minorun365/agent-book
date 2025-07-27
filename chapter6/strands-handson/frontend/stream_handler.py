import streamlit as st
from typing import Dict

def create_state() -> Dict:
    """新しい状態を作成"""
    return {
        "containers": [],
        "current_status": None,
        "current_text": None,
        "final_response": ""
    }

def start_thinking(container, state: Dict):
    """思考開始を表示"""
    with container:
        thinking_status = st.empty()
        thinking_status.status("エージェントが考え中", state="running")
    state["containers"].append((thinking_status, "エージェントが考え中"))

def change_status(event, container, state: Dict):
    """サブエージェントのステータスを更新"""
    progress_info = event["subAgentProgress"]
    message = progress_info.get("message")
    stage = progress_info.get("stage", "processing")
    
    # 前のステータスを完了状態に
    if state["current_status"]:
        status_box, original_message = state["current_status"]
        status_box.status(original_message, state="complete")
    
    # 新しいステータス表示
    with container:
        new_status_box = st.empty()
        display_state = "complete" if stage == "complete" else "running"
        new_status_box.status(message, state=display_state)
    
    status_info = (new_status_box, message)
    state["containers"].append(status_info)
    state["current_status"] = status_info
    state["current_text"] = None
    state["final_response"] = ""

def stream_text(event, container, state: Dict):
    """テキストをストリーミング表示"""
    delta = event["contentBlockDelta"]["delta"]
    if "text" not in delta:
        return
    
    # テキスト出力開始時にステータスを完了に
    if state["current_text"] is None:
        if state["containers"]:
            first_status, first_message = state["containers"][0]
            if "考え中" in first_message:
                first_status.status("エージェントが考え中", state="complete")
        if state["current_status"]:
            status_box, original_message = state["current_status"]
            status_box.status(original_message, state="complete")
    
    # テキスト処理
    text = delta["text"]
    state["final_response"] += text
    
    # テキストコンテナ更新
    if state["current_text"] is None:
        with container:
            state["current_text"] = st.empty()
    if state["current_text"]:
        state["current_text"].markdown(state["final_response"])

def close_display(state: Dict):
    """表示の終了処理"""
    if state["current_text"]:
        state["current_text"].markdown(state["final_response"])
    for status_box, message in state["containers"]:
        status_box.status(message, state="complete")