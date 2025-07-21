# 必要なライブラリをインポート
from strands import Agent
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# エージェントを作成して起動
agent = Agent()
agent("Strandsってどういう意味？")