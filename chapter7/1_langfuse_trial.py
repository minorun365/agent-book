from langchain.chat_models import init_chat_model
from langfuse.langchain import CallbackHandler

from dotenv import load_dotenv
load_dotenv()

# モデルの準備
llm = init_chat_model(
    model="us.anthropic.claude-sonnet-4-20250514-v1:0",
    model_provider="bedrock_converse",
)

# Langfuseのコールバッククラスのインスタンスを生成
langfuse_handler = CallbackHandler()
config={"callbacks": [langfuse_handler]}

# 推論を実行
response = llm.invoke("こんにちは", config=config)
print(response)