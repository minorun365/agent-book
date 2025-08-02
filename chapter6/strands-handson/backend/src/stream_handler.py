import asyncio

async def send_event(queue, message, stage, tool_name=None):
    """サブエージェントのステータスを送信"""
    if not queue:
        return
    
    progress = {"message": message, "stage": stage}
    if tool_name:
        progress["tool_name"] = tool_name
    await queue.put(
        {"event": {"subAgentProgress": progress}}
    )

async def merge_streams(stream, queue):
    """親子エージェントのストリームを統合"""
    create_task = asyncio.create_task
    main = create_task(anext(stream, None))
    sub = create_task(queue.get())
    waiting = {main, sub}
    
    # チャンクの到着を待機
    while waiting:
        ready_chunks, waiting = await asyncio.wait(
            waiting, return_when=asyncio.FIRST_COMPLETED
        )
        for ready_chunk in ready_chunks:
            # 監督者エージェントのチャンクを処理
            if ready_chunk == main:
                event = ready_chunk.result()
                if event is not None:
                    yield event
                    main = create_task(anext(stream, None))
                    waiting.add(main)
                else:
                    main = None
            
            # サブエージェントのチャンクを処理
            elif ready_chunk == sub:
                try:
                    sub_event = ready_chunk.result()
                    yield sub_event
                    sub = create_task(queue.get())
                    waiting.add(sub)
                except Exception:
                    sub = None
        
        if main is None and queue.empty():
            break