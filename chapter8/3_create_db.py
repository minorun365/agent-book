from langchain.embeddings import init_embeddings
from langchain_chroma import Chroma

from dotenv import load_dotenv
load_dotenv()

embedding = init_embeddings(
    model="amazon.titan-embed-text-v2:0",
    provider="bedrock",
)

texts = [
    "AIチャットボットプラットフォーム「SmartChat」(Orion)は自然言語で会話を自動化します。ユーザーの質問に24時間対応するよう設計されています。",
    "リアルタイムデータ可視化サービス「DataVizPro」は大規模データをグラフ表示します。複雑なデータを直感的に把握できるよう提供します。",
    "モバイル決済アプリ「QuickPay」(Falcon)で簡単に支払いを完了できます。セキュアな通信で安全に決済処理が行われます。",
    "社内コラボレーションツール「TeamSync」はタスク共有と進捗管理を支援します。チームメンバーの作業状況を可視化します。",
    "電子契約プラットフォーム「eSignify」(Mercury)で契約書をオンライン署名できます。締結プロセスをスムーズに管理します。",
    "顧客フィードバック収集サービス「FeedGather」はアンケートを自動生成します。収集データを解析しやすい形式で提供します。",
    "NLP要約API「TextSummarize」(Athena)が長文を短く要約します。文章の要点を瞬時に抽出できます。",
    "オンライン学習プラットフォーム「LearnHub」は多彩な教材を配信します。学習進捗をトラッキングしてフィードバックします。",
    "IoTデバイス管理プラットフォーム「DeviceWatch」(Sentinel)で機器を一元監視できます。異常検知アラートを即時に通知します。",
    "クラウドストレージサービス「CloudBox」は大容量ファイルを安全に保存します。データの暗号化とバックアップを自動で実行します。",
]

db = Chroma.from_texts(
    texts=texts,
    embedding=embedding,
    collection_name="service_information",
    persist_directory="./db/chroma_langchain_db"
)