import asyncio

async def send_event(queue, agent_name, message, stage, tool_name=None):
    """サブエージェントのステータスを送信"""
    if not queue:
        return
    
    event = {
        "event": {"subAgentProgress": {"message": message, "stage": stage}}
    }
    if tool_name:
        event["event"]["subAgentProgress"]["tool_name"] = tool_name
    await queue.put(event)

async def merge_streams(stream, stream_queue):
    """親子エージェントのストリームを統合"""
    main_chunk = asyncio.create_task(anext(stream, None))
    sub_chunk = asyncio.create_task(stream_queue.get())
    waiting_chunks = {main_chunk, sub_chunk}
    
    # チャンクの到着を待機
    while waiting_chunks:
        ready_chunks, waiting_chunks = await asyncio.wait(
            waiting_chunks, return_when=asyncio.FIRST_COMPLETED
        )
        
        for ready_chunk in ready_chunks:
            # メインエージェントのチャンクを処理
            if ready_chunk == main_chunk:
                event = ready_chunk.result()
                if event is not None:
                    yield event
                    main_chunk = asyncio.create_task(anext(stream, None))
                    waiting_chunks.add(main_chunk)
                else:
                    main_chunk = None
            
            # サブエージェントのチャンクを処理
            elif ready_chunk == sub_chunk:
                try:
                    sub_event = ready_chunk.result()
                    yield sub_event
                    sub_chunk = asyncio.create_task(stream_queue.get())
                    waiting_chunks.add(sub_chunk)
                except Exception:
                    sub_chunk = None
        
        if main_chunk is None and stream_queue.empty():
            break