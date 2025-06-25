# 第5章 MastaでフルスタックのAIエージェントアプリを作ろう

## ディレクトリ構成

```
.
├── amplify # Amplifyプロジェクト設定
│   ├── auth
│   └── data
├── app
│   ├── api
│   │   └── workflow
│   │       └── execute # ワークフロー実行API
│   ├── components # Next.jsコンポーネント
│   └── types # 型定義
├── lib # Cognito認証関連の共通コード
├── public
└── src
    └── mastra
        ├── agents # Mastraエージェント定義
        ├── tools # Mastraツール定義
        └── workflows # Mastraワークフロー定義
```

