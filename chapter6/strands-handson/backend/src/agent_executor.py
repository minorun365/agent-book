import asyncio
from .stream_handler import send_event

async def _extract_stream(
    queue, agent, event, response_state
):
    """ストリーミングから内容を抽出"""
    if isinstance(event, str):
        response_state["text"] += event
        if queue:
            await queue.put({
                "event": {
                    "contentBlockDelta": {
                        "delta": {"text": event}
                    }
                }
            })
    elif isinstance(event, dict) and "event" in event:
        event_data = event["event"]
        
        # ツール使用を検出
        if "contentBlockStart" in event_data:
            block = event_data["contentBlockStart"]
            start_data = block.get("start", {})
            if "toolUse" in start_data:
                use = start_data["toolUse"]
                tool = use.get("name", "unknown")
                message = f"「{agent}」がツール「{tool}」を実行中"
                await send_event(
                    queue, agent, message, "tool_use", tool
                )
        
        # テキスト増分を処理
        if "contentBlockDelta" in event_data:
            block = event_data["contentBlockDelta"]
            delta = block.get("delta", {})
            if "text" in delta:
                response_state["text"] += delta["text"]
        
        if queue:
            await queue.put(event)

async def invoke_agent(
    agent, query, mcp_client, create_agent, queue
):
    """サブエージェントを呼び出し"""
    response_state = {"text": ""}
    message = f"サブエージェント「{agent}」が呼び出されました"
    await send_event(queue, agent, message, "start")
    
    try:
        # MCPクライアントを起動しながら、エージェントを呼び出し
        with mcp_client:
            agent_obj = create_agent()
            async for event in agent_obj.stream_async(query):
                await _extract_stream(
                    queue, agent, event, response_state
                )
        
        message = f"サブエージェント「{agent}」が調査を完了しました"
        await send_event(queue, agent, message, "complete")
        return response_state["text"]
    
    except Exception:
        return f"{agent}エージェントの処理に失敗しました"