import asyncio
from strands import Agent
from strands_tools import shell
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from .aws_master import aws_master, setup_aws_master
from .strands_master import strands_master, setup_strands_master
from .stream_handler import merge_streams

def _create_orchestrator():
    """監督者エージェントを作成"""
    return Agent(
        model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        tools=[aws_master, strands_master],
        system_prompt="日本語で簡潔に回答してください。"
    )

# アプリケーションを初期化
app = BedrockAgentCoreApp()
orchestrator = _create_orchestrator()

@app.entrypoint
async def invoke(payload):
    """呼び出し処理の開始地点"""
    prompt = payload.get("input", {}).get("prompt", "")
    
    # サブエージェント用のキューを初期化
    queue = asyncio.Queue()
    setup_aws_master(queue)
    setup_strands_master(queue)
    
    try:
        # 監督者エージェントを呼び出し、ストリームを統合
        stream = orchestrator.stream_async(prompt)
        async for event in merge_streams(stream, queue):
            yield event
            
    finally:
        # キューをクリーンアップ
        setup_aws_master(None)
        setup_strands_master(None)

# AgentCoreランタイムを起動
if __name__ == "__main__":
    app.run()