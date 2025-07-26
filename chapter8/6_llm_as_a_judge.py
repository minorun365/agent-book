from ragas.dataset_schema import SingleTurnSample
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import AspectCritic
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
load_dotenv()

user_input = "日本の首都はどこでしょうか？質問に端的に回答してください。"
llm = init_chat_model(
    model="us.anthropic.claude-sonnet-4-20250514-v1:0",
    model_provider="bedrock_converse",
)
response = llm.invoke(("human", user_input)).content
print("response :" + response)

sample = SingleTurnSample(
    user_input=user_input,
    response=response,
    reference="東京都"
)

definition="""
参照データと回答を比較し、正確性を評価してください。
参照データに対して、冗長でなく端的かつ関連した回答ができた場合のみ、評価値を1としてください。
"""

evaluator = AspectCritic(
    name="relevance_score", 
    definition=definition,
    llm=LangchainLLMWrapper(llm)
)

score = evaluator.single_turn_score(sample)
print("Score: " + str(score))