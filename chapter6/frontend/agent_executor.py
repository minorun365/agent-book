import os, json, uuid
import streamlit as st
from stream_handler import (
    create_state, think, change_status, stream, finish
)

def extract(data, container, state):
    """ストリーミングから内容を抽出"""
    if not isinstance(data, dict):
        return

    event = data.get("event", {})    
    if "subAgentProgress" in event:
        change_status(event, container, state)
    elif "contentBlockDelta" in event:
        stream(event, container, state)
    elif "error" in data:
        error_msg = data.get("error", "Unknown error")
        error_type = data.get("error_type", "Unknown")
        st.error(f"AgentCoreエラー: {error_msg}")
        state["final_response"] = f"エラー: {error_msg}"

async def invoke(prompt, container, agent_core):
    """エージェントを呼び出し"""
    state = create_state()
    session_id = f"session_{str(uuid.uuid4())}"
    think(container, state)
    
    try:
        # エージェントの応答を取得
        agent_response = agent_core.invoke_agent_runtime(
            agentRuntimeArn=os.getenv("AGENT_RUNTIME_ARN"),
            runtimeSessionId=session_id,
            payload=json.dumps({
                "input": {
                    "prompt": prompt, "session_id": session_id
                }
            }).encode(),
            qualifier="DEFAULT"
        )
        
        # ストリーミング応答を処理
        for line in agent_response["response"].iter_lines():
            decoded = line.decode("utf-8")
            if not line or not decoded.startswith("data: "):
                continue
            try:
                data = json.loads(decoded[6:])
                extract(data, container, state)
            except json.JSONDecodeError:
                continue
        
        finish(state)
        return state["final_response"]
    
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
        return ""