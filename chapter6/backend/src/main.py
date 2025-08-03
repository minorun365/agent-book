import asyncio
from strands import Agent
from strands_tools import shell
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from .aws_master import aws_master, setup_aws_master
from .api_master import api_master, setup_api_master
from .stream_handler import merge_streams

def _create_orchestrator():
    """監督者エージェントを作成"""
    return Agent(
        model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        tools=[aws_master, api_master],
        system_prompt="""2体のサブエージェントを使って日本語で応対して。
1. AWSマスター：AWSドキュメントなどを参照できます。
2. APIマスター：AWSアカウントをAPIで操作できます。"""
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
    setup_api_master(queue)
    
    try:
        # 監督者エージェントを呼び出し、ストリームを統合
        stream = orchestrator.stream_async(prompt)
        async for event in merge_streams(stream, queue):
            yield event
            
    finally:
        # キューをクリーンアップ
        setup_aws_master(None)
        setup_api_master(None)

# AgentCoreランタイムを起動
if __name__ == "__main__":
    app.run()