import asyncio

async def send_event(
    queue, agent, message, stage, tool=None
):
    """サブエージェントのステータスを送信"""
    if not queue:
        return
    
    progress = {"message": message, "stage": stage}
    event = {"event": {"subAgentProgress": progress}}
    if tool:
        progress["tool_name"] = tool
    await queue.put(event)

async def merge_streams(stream, queue):
    """親子エージェントのストリームを統合"""
    next_item = anext(stream, None)
    main = asyncio.create_task(next_item)
    sub = asyncio.create_task(queue.get())
    waiting = {main, sub}
    
    # チャンクの到着を待機
    while waiting:
        ready, waiting = await asyncio.wait(
            waiting, return_when=asyncio.FIRST_COMPLETED
        )
        
        for chunk in ready:
            # メインエージェントのチャンクを処理
            if chunk == main:
                event = chunk.result()
                if event is not None:
                    yield event
                    next_item = anext(stream, None)
                    main = asyncio.create_task(next_item)
                    waiting.add(main)
                else:
                    main = None
            
            # サブエージェントのチャンクを処理
            elif chunk == sub:
                try:
                    sub_event = chunk.result()
                    yield sub_event
                    sub = asyncio.create_task(queue.get())
                    waiting.add(sub)
                except Exception:
                    sub = None
        
        if main is None and queue.empty():
            break