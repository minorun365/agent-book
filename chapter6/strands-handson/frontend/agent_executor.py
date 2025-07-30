import os, json, uuid
import streamlit as st
from stream_handler import (
    create_state, start_thinking, change_status,
    stream_text, close_display
)

def extract_stream(data, container, state):
    """ストリーミングから内容を抽出"""
    if not isinstance(data, dict):
        return

    event = data.get("event", {})    
    if "subAgentProgress" in event:
        change_status(event, container, state)
    elif "contentBlockDelta" in event:
        stream_text(event, container, state)
    elif "error" in data:
        error_msg = data.get("error", "Unknown error")
        error_type = data.get("error_type", "Unknown")
        st.error(f"AgentCoreエラー: {error_msg}")
        state["final_response"] = f"エラー: {error_msg}"

async def invoke_agent(prompt, container, agent_core):
    """エージェントを呼び出し"""
    state = create_state()
    session_id = f"session_{str(uuid.uuid4())}"
    start_thinking(container, state)
    
    payload = json.dumps({
        "input": {"prompt": prompt, "session_id": session_id}
    }).encode()
    
    try:
        agent_response = agent_core.invoke_agent_runtime(
            agentRuntimeArn=os.getenv("AGENT_RUNTIME_ARN"),
            runtimeSessionId=session_id,
            payload=payload,
            qualifier="DEFAULT"
        )
        for line in agent_response["response"].iter_lines():
            decoded = line.decode("utf-8")
            if not line or not decoded.startswith("data: "):
                continue
            try:
                data = json.loads(decoded[6:])
                extract_stream(data, container, state)
            except json.JSONDecodeError:
                continue
        
        close_display(state)
        return state["final_response"]
    
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
        return ""