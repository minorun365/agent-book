import boto3
import os
from langfuse import observe
from tavily import TavilyClient

from dotenv import load_dotenv
load_dotenv()

# Amazon Bedrockを呼び出すために利用
bedrock_client = boto3.client("bedrock-runtime")
model_id = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"

# Web検索クエリを作成する関数
@observe
def create_query(query):
    system_prompt = """ユーザからの問い合わせ内容をWeb検索し、レポートを作成します。
    Web検索用のクエリを1つ作成してください。検索単語以外は回答しないでください。"""
    
    prompt= f"ユーザの質問: {query}"

    system = [
        {"text": system_prompt}
    ]
    messages = [
        {
            "role": "user",
            "content": [{"text": prompt}],
        }
    ]
    response = bedrock_client.converse(
        modelId=model_id,
        system=system,
        messages=messages
    )
    return response["output"]["message"]["content"][0]["text"]

# Tavilyを使ったWeb検索を実行する関数
tavily_client = TavilyClient(api_key=os.environ.get('TAVILY_API_KEY'))
@observe
def web_search(query: str):
    """Get content related the query from web."""
    search_result = tavily_client.search(
        query=query,
        max_results=3
    )
    return [doc["content"] for doc in search_result["results"]]

# Web検索結果をMarkdownレポートに要約する関数
@observe
def create_report(query: str, contents: list[str]):
    system_prompt = """Web検索した結果とユーザクエリを元にMarkdownのレポートを作成してください。
    タイトルと見出しも作成してください"""
    
    prompt= f"ユーザの質問: {query}\n\n web検索結果: {"\n".join(contents)}"

    system = [
        {"text": system_prompt}
    ]
    messages = [
        {
            "role": "user",
            "content": [{"text": prompt}],
        }
    ]

    response = bedrock_client.converse(
        modelId=model_id,
        system=system,
        messages=messages
    )
    return response["output"]["message"]["content"][0]["text"]

# 各タスクを呼び出す関数
@observe
def workflow(query: str):
    web_query = create_query(query)
    contents = web_search(web_query)
    report = create_report(web_query, contents)

    return report

# ユーザークエリ
query = "LangChainとLangGraphのユースケースの違いについて教えてください。"

report = workflow(query)
print(report)
