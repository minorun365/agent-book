import asyncio
from strands import Agent
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from aws_kb_agent import aws_kb_agent, setup_kb_agent
from aws_api_agent import aws_api_agent, setup_api_agent
from stream_handler import merge_streams

def _create_orchestrator():
    """メインエージェントを作成"""
    return Agent(
        model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        tools=[aws_kb_agent, aws_api_agent],
        system_prompt="""2つのサブエージェントを使えます。
1. AWSナレッジエージェント: AWSドキュメント等から情報を検索
2. AWS APIエージェント: AWSアカウントをAPI操作
API操作を行う前に、必ずAWSナレッジで情報収集してください。"""
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
    setup_kb_agent(queue)
    setup_api_agent(queue)
    
    try:
        # メインエージェントを呼び出し、ストリームを統合
        stream = orchestrator.stream_async(prompt)
        async for event in merge_streams(stream, queue):
            yield event
            
    finally:
        # キューをクリーンアップ
        setup_kb_agent(None)
        setup_api_agent(None)

# AgentCoreランタイムを起動
if __name__ == "__main__":
    app.run()