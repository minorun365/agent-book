# 必要なライブラリをインポート
from agents import Agent, Runner, function_tool
import asyncio

# ツールを定義
@function_tool
async def add_numbers(a: int, b: int):
   return a + b

# エージェントを作成
addition_agent = Agent(
   name="計算エージェント",
   handoff_description="足し算専門のエージェント",
   instructions="足し算ツールを使って計算してください。",
   tools=[add_numbers]
)

# メイン関数
async def main():
   # エージェントを実行
   result = await Runner.run(addition_agent, "2足す3は？")
   print(result.final_output)

# メイン関数を非同期実行
asyncio.run(main())