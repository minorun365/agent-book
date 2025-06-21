import boto3
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# Bedrock用のAPIクライアントを作成
client = boto3.client("bedrock-runtime")

# Converse APIを実行
response = client.converse(
    modelId="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    messages=[{
        "role": "user",
        "content": [{"text": "こんにちは"}]
    }]
)

# 実行結果を画面に表示
print(response["output"]["message"]["content"][0]["text"])