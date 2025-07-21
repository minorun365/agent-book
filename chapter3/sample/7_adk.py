from google.adk.agents import Agent

# ツールを定義
def add_numbers(a: int, b: int) -> dict:
   result = a + b
   return {
       "status": "success",
       "result": result
   }

# エージェントを作成
root_agent = Agent(
   name="計算エージェント",
   description="自然言語の指示から計算を行います",
   instruction="足し算ツールを使って計算してください",
   model="gemini-2.0-flash",
   tools=[add_numbers],
)