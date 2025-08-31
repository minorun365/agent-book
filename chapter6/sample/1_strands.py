from dotenv import load_dotenv
from strands import Agent, tool
from strands_tools import calculator

load_dotenv()

# サブエージェント1を定義
@tool
def math_agent(query: str) -> str:
    agent = Agent(
        model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        system_prompt="ツールを使って計算を行ってください",
        tools=[calculator]
    )
    return str(agent(query))

# サブエージェント2を定義
@tool
def haiku_agent(query: str) -> str:
    agent = Agent(
        model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        system_prompt="与えられたお題で五・七・五の俳句を詠んで"
    )
    return str(agent(query))

# 監督者エージェントの作成と実行
orchestrator = Agent(
    model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    system_prompt="与えられた問題を計算して、答えを俳句として詠んで",
    tools=[math_agent, haiku_agent]
)
orchestrator("十円持っている太郎くんが二十円もらいました。今いくら？")