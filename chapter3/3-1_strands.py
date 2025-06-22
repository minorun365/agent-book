# 必要なライブラリをインポート
from strands import Agent
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# エージェントの作成
agent = Agent()

# エージェントの起動
agent("Strandsってどういう意味？")