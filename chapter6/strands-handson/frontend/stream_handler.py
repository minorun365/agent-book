import streamlit as st

def create_state():
    """新しい状態を作成"""
    return {
        "containers": [],
        "current_status": None,
        "current_text": None,
        "final_response": ""
    }

def start_thinking(container, state):
    """思考開始を表示"""
    with container:
        status = st.empty()
        status.status("考え中", state="running")
    state["containers"].append((status, "考え中"))

def change_status(event, container, state):
    """サブエージェントのステータスを更新"""
    progress_info = event["subAgentProgress"]
    message = progress_info.get("message")
    stage = progress_info.get("stage", "processing")
    
    # 前のステータスを完了状態に
    if state["current_status"]:
        status, prev_message = state["current_status"]
        status.status(prev_message, state="complete")
    
    # 新しいステータス表示
    with container:
        status = st.empty()
        if stage == "complete":
            status.status(message, state="complete")
        else:
            status.status(message, state="running")
    
    status_info = (status, message)
    state["containers"].append(status_info)
    state["current_status"] = status_info
    state["current_text"] = None
    state["final_response"] = ""

def stream_text(event, container, state):
    """テキストをストリーミング表示"""
    delta = event["contentBlockDelta"]["delta"]
    if "text" not in delta:
        return
    
    # テキスト出力開始時にステータスを完了に
    if state["current_text"] is None:
        if state["containers"]:
            status, message = state["containers"][0]
            if "考え中" in message:
                status.status("考え中", state="complete")
        if state["current_status"]:
            status, message = state["current_status"]
            status.status(message, state="complete")
    
    # テキスト処理
    text = delta["text"]
    state["final_response"] += text
    
    # テキストコンテナ更新
    if state["current_text"] is None:
        with container:
            state["current_text"] = st.empty()
    if state["current_text"]:
        current = state["current_text"]
        current.markdown(state["final_response"])

def close_display(state):
    """表示の終了処理"""
    if state["current_text"]:
        current = state["current_text"]
        current.markdown(state["final_response"])
    for status, message in state["containers"]:
        status.status(message, state="complete")