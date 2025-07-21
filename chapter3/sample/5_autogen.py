# 必要なライブラリをインポート
import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

# ツールを定義
async def add_numbers(a: int, b: int):
   return a + b

# メイン関数
async def main():
   # エージェントを作成
   agent = AssistantAgent(
       name="計算エージェント",
       model_client=OpenAIChatCompletionClient(model="gpt-4o"),
       system_message="足し算ツールを使って計算してください。",
       tools=[add_numbers]
   )

   # エージェントを実行
   response = await agent.run(task="2足す3は？")
   print(response)

# メイン関数を非同期実行
asyncio.run(main())