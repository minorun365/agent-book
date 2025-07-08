
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_tavily import TavilySearch
from langfuse import get_client
from langfuse.langchain import CallbackHandler
from langgraph.prebuilt import create_react_agent

# 環境変数の読み込み
from dotenv import load_dotenv
load_dotenv("/workspaces/agent-book/.env")

# ReActエージェントの構築
def create_agent(model : str, temperature: float):
    # LLMを定義
    llm = init_chat_model(
        model=model,
        model_provider="bedrock_converse",
        temperature=temperature
    )
    # ツールの定義
    tools = [TavilySearch(max_results=2, topic="general")]
    # ReActエージェントの作成
    return create_react_agent(llm, tools)

langfuse = get_client()

prompt_template = langfuse.get_prompt("ai-agent", type="chat", label="latest")
model = prompt_template.config["model"]
temperature = prompt_template.config["temperature"]

langchain_prompt = ChatPromptTemplate(prompt_template.get_langchain_prompt())
messagses = langchain_prompt.invoke({"city": "横浜"})

# ReactAgentの実行
agent = create_agent(model, temperature)

langfuse_handler = CallbackHandler()
response = agent.invoke(
    messagses,
    config={"callbacks": [langfuse_handler]}
)
for message in response["messages"]:
    message.pretty_print()

