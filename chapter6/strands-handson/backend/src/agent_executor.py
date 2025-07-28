import asyncio
from .stream_handler import send_event

async def _extract_stream(queue, agent_name, event, response_state):
    """ストリーミングから内容を抽出"""
    if isinstance(event, str):
        response_state["text"] += event
        if queue:
            await queue.put({
                "event": {"contentBlockDelta": {"delta": {"text": event}}}
            })
    elif isinstance(event, dict) and "event" in event:
        event_data = event["event"]
        
        # ツール使用を検出
        if "contentBlockStart" in event_data:
            start_data = event_data["contentBlockStart"].get("start", {})
            if "toolUse" in start_data:
                tool_name = start_data["toolUse"].get("name", "unknown")
                await send_event(queue, agent_name, 
                    f"サブエージェント「{agent_name}」がツール「{tool_name}」を実行中", 
                    "tool_use", tool_name
                )
        
        # テキスト増分を処理
        if "contentBlockDelta" in event_data:
            delta = event_data["contentBlockDelta"].get("delta", {})
            if "text" in delta:
                response_state["text"] += delta["text"]
        
        if queue:
            await queue.put(event)

async def invoke_agent(agent_name, query, mcp_client, create_agent, queue):
    """サブエージェントを呼び出し"""
    response_state = {"text": ""}
    await send_event(
        queue, agent_name,
        f"サブエージェント「{agent_name}」が呼び出されました", "start"
    )
    
    try:
        # MCPクライアントを起動しながら、エージェントを呼び出し
        with mcp_client:
            agent = create_agent()
            async for event in agent.stream_async(query):
                await _extract_stream(queue, agent_name, event, response_state)
        
        await send_event(
            queue, agent_name,
            f"サブエージェント「{agent_name}」が調査を完了しました", "complete"
        )
        return response_state["text"]
    
    except Exception:
        return f"{agent_name}エージェントの処理に失敗しました"