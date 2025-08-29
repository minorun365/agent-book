from dotenv import load_dotenv
from strands import Agent
from strands.multiagent.a2a import A2AServer

load_dotenv()

# リモートエージェントを作成
agent = Agent(
    name="俳句エージェント",
    description="お題に沿った俳句を読みます。"
)

# 上記エージェントをA2Aサーバーとして起動
a2a_server = A2AServer(agent=agent)
a2a_server.serve()