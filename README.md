# W&B ハンズオンアセット集

[English](README_EN.md)

このリポジトリは、Weights & Biases (W&B) のハンズオンで利用するサンプルコード、ノートブック、設定ファイル、評価用アセットをまとめたものです。W&B Models、W&B Weave、W&B Training などを題材に、実験管理、LLMアプリケーションのトレーシング、評価、モニタリング、Agentic RL までを実際に動かしながら学べます。

各ハンズオンは基本的に独立したディレクトリまたはノートブックとして配置されています。詳しいセットアップや実行方法は、それぞれのREADMEを参照してください。

## ハンズオン一覧

| ハンズオン | 場所 | 内容 |
| --- | --- | --- |
| W&B Models 101 | [models/W&B_models_intro_notebook.ipynb](models/W%26B_models_intro_notebook.ipynb) | `wandb` ライブラリのログイン、Run作成、メトリクス・メディアのログ、Table、Artifacts、データとモデルの系譜管理を学ぶ入門ノートブックです。 |
| Weave Introduction Hands-on | [weave_introduction_handson/](weave_introduction_handson/) | W&B Weave を使い、LLMアプリケーションのトレーシング、プロンプト・データセット・モデル・Scorerの管理、オフライン評価、オンラインフィードバック、ガードレール、モニタリングを学びます。日本語版と英語版のスクリプトがあります。 |
| eSIM Agent Demo | [esim-agent-demo/](esim-agent-demo/) | OpenAI Agents SDK と W&B Weave を使った、eSIMサービス向けマルチエージェントデモです。プラン検索、予約、RAG Q&A、ガードレール、Weaveによるトレース、評価シナリオとScorerを含みます。 |
| ART-E: Email Search Agent | [ART-E/](ART-E/) | Enronメールデータセットを使い、メール検索エージェントをAgentic RLで学習するハンズオンです。ART、W&B Training / Serverless RL、W&B / Weaveによるログ記録、学習済みモデルの推論評価を扱います。 |
