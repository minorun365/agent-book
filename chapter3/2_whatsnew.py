# 必要なライブラリをインポート
import feedparser
from strands import Agent, tool
from dotenv import load_dotenv

# 環境変数を読み込む
load_dotenv()

# ツールを定義
@tool
def get_aws_updates(service_name: str) -> str:
    # AWS What's NewのRSSフィードをパース
    feed = feedparser.parse("https://aws.amazon.com/about-aws/whats-new/recent/feed/")    
    result = []

    # フィードの各エントリをチェック
    for entry in feed.entries:
        # 件名にサービス名が含まれているかチェック
        if service_name.lower() in entry.title.lower():
            result.append({
                "published": entry.get("published", "N/A"),
                "summary": entry.get("summary", "")
            })
            
            # 最大3件のエントリを取得
            if len(result) >= 3:
                break

    return result

# エージェントを作成
agent = Agent(
    model="us.anthropic.claude-3-5-haiku-20241022-v1:0",
    tools=[get_aws_updates]
)

# ユーザー入力を取得
service_name = input("アップデートを知りたいAWSサービス名を入力してください: ").strip()

# プロンプトを指定してエージェントを起動
prompt = f"AWSの{service_name}の最新アップデートを、日付つきで要約して。"
response = agent(prompt)