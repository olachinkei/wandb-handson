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

## Advanced Topic: coding agentで次の改善の一手を試す

ハンズオンを一通り実行したら、[wandb/skills](https://github.com/wandb/skills) をインストールしたcoding agentに、W&BのRun、Trace、Evaluation結果を見ながら次の改善案を考えさせ、実装と再評価まで試させることができます。

```bash
npx skills add wandb/skills
export WANDB_API_KEY=<your-key>
```

おすすめの流れ:

1. 取り組むハンズオンのディレクトリを開き、READMEに従ってサンプルや評価を一度実行します。
2. W&B UIまたはWeave UIで、Run、Trace、Evaluationの結果が記録されていることを確認します。
3. coding agentに「このプロジェクトのW&B/Weaveの結果を見て、次に改善すべき一手を提案し、最小変更で試してください」と依頼します。
4. agentが提案した改善を1つ選び、コード変更、再実行、Before/Afterの比較まで行います。
5. 改善が有効ならREADMEや評価シナリオに反映し、効果が薄ければTraceやScorerを見直して次の仮説を立てます。

例:

```text
このeSIM Agent DemoのWeave TraceとEvaluation結果を確認して、
失敗しやすいケースを1つ特定し、最小限のコード変更で改善してください。
変更後に評価を再実行し、Before/Afterを説明してください。
```
