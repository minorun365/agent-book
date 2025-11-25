# 書籍「AIエージェント開発/運用入門」サンプルコード

標記書籍のハンズオン用コードや、アップデートのお知らせなどを本リポジトリで公開します。

https://www.sbcr.jp/product/4815636609/

<img height="300" alt="書影" src="https://www.sbcr.jp/wp-content/uploads/2025/07/AAP_AI%E3%82%A8%E3%83%BC%E3%82%B7%E3%82%99%E3%82%A7%E3%83%B3%E3%83%88%E9%96%8B%E7%99%BA%E9%81%8B%E7%94%A8%E5%85%A5%E9%96%80_D1-1-scaled.jpg" />


## 📣 新着のお知らせ（詳細は後述）

- 【2025/11/25更新】第4章 AWSの仕様変更により4.3のハンズオンでエラーが出るようになったため、サンプルコード修正しました。
- 【2025/11/2更新】第5章 Mastraのインストールコマンドに誤植がありました（第3刷のみ）。
- 【2025/10/28更新】第5章 Mastraのインストールコマンドを更新しました。
- 【2025/10/17更新】付録 Bedrockのクォータ緩和申請手順の変更内容を補足しました。
- 【2025/10/16更新】第2章 Bedrockのモデルアクセス有効化手順の変更内容を補足しました。
- 【2025/10/4更新】第3章 VoltAgentのV1リリースに伴い、サンプルコードを更新しました。


## 💻 サンプルコードの使い方

各チャプター名のディレクトリ配下に、書籍内のサンプルコードを格納しています。コードの打ち間違いによるエラーを防ぐためにも、コピペ用にぜひ活用ください。


## 🆘 エラー等でハンズオンが進められないときは

[Issues](https://github.com/minorun365/agent-book/issues) より、テンプレートを使って問い合わせを投稿ください。著者陣がベストエフォートで解決のお手伝いをさせていただきます。


## 📗 お知らせ詳細

### 第2章

- P.36： 2.2.2冒頭のmemoに記載のように、Bedrockのモデルアクセス有効化手順が変更されました。AWSマネジメントコンソールからAmazon Bedrockのサービス画面へ移動したら、左サイドバーの「チャット/テキストのプレイグラウンド」にアクセスして、AnthropicのClaude Sonnet 4.5モデルを選択します。すると、ユースケースの提出フォームが表示されるため、本書P.38の記載に従って内容を記入し送信してください。2〜3分で、すべてのAnthropicモデルが利用可能となります。手順の詳細は[こちら](https://qiita.com/minorun365/items/7070a0206547cc6dc650)にも記載しています。

### 第3章

- P.60： 9/16にVoltAgent V1がリリースされました。Agentクラスから `llm` オプションが削除されたことに加え、VoltAgentクラスでサーバーの組み込みが必要となったため、[サンプルコード](https://github.com/minorun365/agent-book/blob/main/chapter3/sample/4_voltagent.ts)を更新しています。気づいてくださった[chiaoi](https://x.com/_chiaoi)さん、ありがとうございます！（参考：[公式ドキュメント](https://voltagent.dev/docs/getting-started/migration-guide/)）

### 第4章

- P.122： 11/23頃から、4.3のハンズオン[コード](https://github.com/minorun365/agent-book/blob/main/chapter4/3_mcp_agent.py)を実行すると、BedrockのConverse APIからバリデーションエラーが返るようになりました。LangChain側に[バグ報告](https://github.com/langchain-ai/langchain-aws/issues/775)も上がっているので、今後のアップデートで修正される可能性もありますが、とり急ぎエラーが起きないよう、本書の[サンプルコード](https://github.com/minorun365/agent-book/blob/main/chapter4/3_mcp_agent.py)を暫定修正済みです。45-56行目のコードを追加してお使いください。気づいてくださった[TasukuMatsuura](https://github.com/TasukuMatsuura)さん、ありがとうございます！

### 第5章

- P.162/197： Mastra関連ライブラリのバージョンアップに伴い、インストールコマンドを一部更新しました。[コピペ用のコマンドファイル](https://github.com/minorun365/agent-book/blob/main/chapter5/%E3%82%B3%E3%83%94%E3%83%9A%E7%94%A8%E3%82%B3%E3%83%9E%E3%83%B3%E3%83%89.md)を参照ください。気づいてくださった[ytak-sagit](https://github.com/ytak-sagit)さん、ありがとうございます！
- P.162： 第3刷のみ、Mastraのインストールコマンドに1箇所誤植がありました。`npx mastra init@0.11.3` ではなく `npx mastra@0.11.3 init` が正となります。本GitHub上のコピペ用コマンドは修正済みのため、こちらを利用いただければ問題ありません。気づいてくださった[Koichi](https://github.com/Koichi73)さん、ありがとうございます！

### 付録

- P.389： 付録1.3のBedrockクォータ緩和申請手順が、AWSのアップデートにより簡単になりました。サポートケースの起票が不要になり、Service Quotasメニューから引き上げリクエストが可能です。手順は[こちら](https://qiita.com/minorun365/items/bc58bbb2490ef1b5fdee)を参照ください。


## 🥰 読者のみなさまのブログ紹介

素敵な感想・書評をどうもありがとうございます！！

- 熊田さん [【書評】『AIエージェント開発/運用入門』これからAIエージェント開発を始めたいエンジニアへ](https://qiita.com/hedgehog051/items/ca64f9958addebc58cf9)
- ニケちゃん [AIエージェントこれからやりたい人とすでにやってる人向けの書籍紹介（つまり全員）｜ニケちゃん](https://note.com/nike_cha_n/n/nc4c17567f5f0)
- おむろんさん1 [書籍「AIエージェント開発/運用入門」を献本いただきました！ - omuronの備忘録](https://omuron.hateblo.jp/entry/2025/10/01/000000)
- おむろんさん2 [書籍「AIエージェント開発/運用入門」を献本いただきました！ - omuronの備忘録](https://omuron.hateblo.jp/entry/2025/10/01/000000)
- からあげさん [AIエージェント関連書籍4冊を徹底比較 - karaage. [からあげ]](https://karaage.hatenadiary.jp/entry/2025/10/01/073000)
- ふくちさん [書籍「AIエージェント開発/運用入門」のレビューへ参加させていただきました！](https://qiita.com/har1101/items/d070a6b8181f24ed6697)
- たけさん [書籍「AIエージェント開発/運用入門」をやってみる。その１｜のんびりと](https://note.com/bnctake/n/naf36facb7287)
- ツカジーさん [【良書】「AIエージェント開発/運用入門」のハンズオンをやってみた](https://qiita.com/zzzzico/items/23c2b4e04ffb1d111000)
