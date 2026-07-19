# 必要なライブラリをインポート
import feedparser
import streamlit as st
from strands import Agent, tool
from dotenv import load_dotenv

# 環境変数を読み込む
load_dotenv()

# ツールを定義
@tool
def get_aws_updates(service_name: str) -> list:
    # AWS What's NewのRSSフィードをパース
    feed = feedparser.parse("https://aws.amazon.com/about-aws/whats-new/recent/feed/")
    result = []

    # フィードの各エントリをチェック
    for entry in feed.entries:
        # 件名にサービス名が含まれているかチェック
        title = entry.get("title", "")
        if isinstance(title, str) and service_name.lower() in title.lower():
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
    model="us.anthropic.claude-sonnet-4-6",
    tools=[get_aws_updates]
)

# ページタイトルと入力欄を表示
st.title("AWSアップデート確認くん（同期版）")
service_name = st.text_input("アップデートを知りたいAWSサービス名を入力してください：")

# ボタンを押したら生成開始
if st.button("確認"):
    if service_name:
        with st.spinner("アップデートを確認中..."):
            prompt = f"AWSの{service_name.strip()}の最新アップデートを、日付つきで要約して。"

            # 同期呼び出し（asyncio不要）
            result = agent(prompt)

        # 処理完了後にまとめて表示
        st.markdown(str(result))
