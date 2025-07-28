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

async def invoke_agent(prompt, container, core):
    """エージェントを呼び出し"""
    state = create_state()
    session_id = f"session_{str(uuid.uuid4())}"
    start_thinking(container, state)
    
    payload = json.dumps({
        "input": {
            "prompt": prompt, "session_id": session_id
        }
    }).encode()
    
    try:
        arn = os.getenv("AGENT_RUNTIME_ARN")
        response = core.invoke_agent_runtime(
            agentRuntimeArn=arn,
            runtimeSessionId=session_id,
            payload=payload,
            qualifier="DEFAULT"
        )
        for line in response["response"].iter_lines():
            decoded = line.decode("utf-8")
            if line and decoded.startswith("data: "):
                try:
                    data = json.loads(decoded[6:])
                    extract_stream(data, container, state)
                except json.JSONDecodeError:
                    continue
            else:
                continue
        
        close_display(state)
        return state["final_response"]
    
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
        return ""