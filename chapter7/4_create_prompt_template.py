from langfuse import get_client
from dotenv import load_dotenv
load_dotenv()

langfuse = get_client()
 
# Langfuseのプロンプトテンプレートを作成する
langfuse.create_prompt(
    name="ai-agent",
    type="chat",
    prompt=[
        {"role": "user", "content": "{{city}}の人口は？"}
    ],
    config={
        "model": "us.anthropic.claude-sonnet-4-20250514-v1:0",
        "temperature": 1,
    }
)