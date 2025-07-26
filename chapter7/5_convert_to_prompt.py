
from langfuse import get_client
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
load_dotenv()

langfuse = get_client()
prompt_template = langfuse.get_prompt("ai-agent", type="chat", label="latest")

langchain_prompt = ChatPromptTemplate(prompt_template.get_langchain_prompt())
messagses = langchain_prompt.invoke({"city": "東京都"})
print(messagses)