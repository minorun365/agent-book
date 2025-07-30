from strands import Agent
from strands_tools.a2a_client import A2AClientToolProvider

# A2Aサーバーをツールに変換
provider = A2AClientToolProvider(
    known_agent_urls=["http://localhost:9000"]
)

# クライアントエージェントを作成して実行
agent = Agent(tools=provider.tools)
response = agent("Strandsにちなんだ俳句を詠んで")