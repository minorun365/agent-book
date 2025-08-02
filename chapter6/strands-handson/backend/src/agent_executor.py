import asyncio
from .stream_handler import send_event

async def extract(queue, agent, event, state):
    """ストリーミングから内容を抽出"""
    if isinstance(event, str):
        state["text"] += event
        if queue:
            delta = {"delta": {"text": event}}
            await queue.put(
                {"event": {"contentBlockDelta": delta}}
            )
    elif isinstance(event, dict) and "event" in event:
        event_data = event["event"]
        
        # ツール使用を検出
        if "contentBlockStart" in event_data:
            block = event_data["contentBlockStart"]
            start_data = block.get("start", {})
            if "toolUse" in start_data:
                tool_use = start_data["toolUse"]
                tool = tool_use.get("name", "unknown")
                await send_event(queue, 
                    f"「{agent}」がツール「{tool}」を実行中", "tool_use", tool
                )
        
        # テキスト増分を処理
        if "contentBlockDelta" in event_data:
            block = event_data["contentBlockDelta"]
            delta = block.get("delta", {})
            if "text" in delta:
                state["text"] += delta["text"]
        
        if queue:
            await queue.put(event)

async def invoke(agent, query, mcp, create_agent, queue):
    """サブエージェントを呼び出し"""
    state = {"text": ""}
    await send_event(
        queue, f"サブエージェント「{agent}」が呼び出されました", "start"
    )
    
    try:
        # MCPクライアントを起動しながら、エージェントを呼び出し
        with mcp:
            agent_obj = create_agent()
            async for event in agent_obj.stream_async(query):
                await extract(queue, agent, event, state)
        
        await send_event(
            queue, f"「{agent}」が対応を完了しました", "complete"
        )
        return state["text"]
    
    except Exception:
        return f"{agent}エージェントの処理に失敗しました"