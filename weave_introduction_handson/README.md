# Weave Introduction Hands-on

W&B Weave を使った Trace、評価、モニタリングのハンズオンです。

## Weave を初めて聞いたという方へ

Weave の機能や価値については、[こちらのページ](https://note.com/wandb_jp/n/n94100f3961fc)にまとめています。

## W&B のアカウント発行・環境構築方法

[こちらのページ](https://wandbai.notion.site/W-B-Models-Weave-22dad8882177429ba1e9f0f05e7ceac3?source=copy_link)に、W&B のアカウント発行方法・環境構築方法を記載しています。手順に従って、W&B アカウントの発行と API キーの取得を行ってください。

利用している環境によって、アカウント発行方法が異なります。

- **W&B Multitenant SaaS を利用する場合**
  - [https://www.wandb.jp/](https://www.wandb.jp/) にアクセスし、右上のサインアップボタンからアカウントを作成してください。
- **Dedicated Cloud またはオンプレミス環境を利用する場合**
  - 管理者がユーザーアカウントを発行します。ユーザーの方は、管理者にアカウント発行を依頼してください。
  - アカウント発行後に届くメール内のリンクからログインしてください。
  - 環境変数 `WANDB_BASE_URL` を、W&B から案内された URL に設定してください。
  - ログインできない場合、`WANDB_BASE_URL` が未設定であることがよくあります。URL がわからない場合は、管理者または担当の W&B エンジニアに確認してください。


**Teamによる作業環境管理**

W&B では、Team、Project、Run (W&B Models)、Trace (W&B Weave) という単位で実験を管理します。Team は共同作業の単位で、同じ Team に所属するメンバーには実験結果が共有されます。Project は Team 配下のフォルダのような管理単位です。

Enterprise 環境では、Team の作成は Admin のみが行えます。既存の Team 名を Admin に確認するか、新しい Team の作成を依頼してください。Free plan では作成できる Team は 1 つです。

<img src="img/whatisteam.png" alt="Team とは" width="640">

## ハンズオン Agenda

### 1. Tracing (トレーシング)

- `1_1` 基本的なトレーシング (@weave.op, Library Integration, エラートラッキング)
- `1_2` Agent SDK (ツール呼び出し, Threads)
- `1_3` マルチモーダル - OpenAI (画像, 音声, PDF)
- `1_4` 高度なトレーシング (Display Name, Attributes, PII Redaction, Sampling)

**補足: Agent 向け Trace について**

Agent アプリケーションでは、LLM 呼び出しだけでなく、ツール実行、サブタスク、複数ステップの意思決定をまとめて追跡できることが重要です。Weave では Agent 向け Trace の新機能が開発されており、現時点では Public Preview として提供されています。

このハンズオンの `1_2` では OpenAI Agents SDK と Weave の基本的な連携を扱います。Public Preview の Agent Trace 機能については、最新の仕様が変わる可能性があるため、利用する場合は [Agent 向け Trace の公式ドキュメント](https://docs.wandb.ai/weave/guides/tracking/trace-agents) を確認してください。

### 2. Asset Management (アセット管理)

- `2_1_assets` アセット管理と Scorer 作成 (Model, Prompt, Dataset, Scorer)

### 3. Evaluation (評価)

- `3_1` オフライン評価 (`weave.Evaluation`, 複数 Scorer)
- `3_2` EvaluationLogger (柔軟なバッチ評価)
- `3_3` アノテーションキュー (Annotation Queue / Review: [ドキュメント](https://docs.wandb.ai/weave/guides/tracking/annotation-review#annotation-workflow))
### 4. Monitoring (モニタリング)

- `4_1` オンラインフィードバック (Reaction, Note, カスタムフィードバック)
- `4_2` ガードレールとモニタリング (Scorer をガードレールとして使用)
- `4_3` Monitors (本番環境の Trace を Scorer / built-in signals で継続評価: [ドキュメント](https://docs.wandb.ai/weave/guides/evaluation/monitors))

### 5. その他便利な機能

- `5_1` W&B Skills / MCP (AI エージェントから W&B / Weave を参照: [Skills](https://github.com/wandb/skills), [MCP Server](https://docs.wandb.ai/platform/mcp-server))
- `5_2` Automations (Monitor metrics や Trace activity に応じた通知・アクション: [ドキュメント](https://docs.wandb.ai/weave/guides/evaluation/automations))
- `5_3` Dynamic Leaderboards (Evaluation 結果を継続的に比較するビュー: [ドキュメント](https://docs.wandb.ai/weave/guides/evaluation/dynamic_leaderboards))
- `5_4` Trace Plots (cost、latency、token usage の可視化: [ドキュメント](https://docs.wandb.ai/weave/guides/tracking/trace-plots))
- `5_5` Saved Views (Trace / Eval の filter、sort、columns を保存: [ドキュメント](https://docs.wandb.ai/weave/guides/tools/saved-views))
- `5_6` Playground (Trace からプロンプトやモデル設定を再実験: [ドキュメント](https://docs.wandb.ai/weave/guides/tools/playground#use-the-playground-to-experiment-with-prompts))

## 環境構築・実行方法

ハンズオンを始める前に、環境が正しくセットアップされているか確認してください。

### 確認手順

**1. プロジェクトディレクトリに移動**

```bash
cd weave_introduction_handson
```

**2. 環境変数を設定**

W&B と OpenAI の API キーを取得したら、環境変数を設定します。ローカルで実行する場合は、プロジェクト直下に `.env` ファイルを作成するのが簡単です。

```env
# 必須
WANDB_API_KEY=your_wandb_api_key
OPENAI_API_KEY=your_openai_api_key

# オプション
WANDB_ENTITY=your_team_name
WANDB_PROJECT=weave-handson

# Dedicated Cloud やオンプレミスを利用している場合
WANDB_BASE_URL=https://your-instance.wandb.io
```

**注意:** Dedicated Cloud やオンプレミス環境を利用している場合は、`WANDB_BASE_URL` に自社インスタンスの URL を設定してください。

**その他の便利な環境変数:**

詳細: [公式ドキュメント](https://docs.wandb.ai/weave/guides/core-types/env-vars)

| 変数名 | デフォルト | 説明 |
| --- | --- | --- |
| `WEAVE_DISABLED` | `false` | トレーシング無効化 |
| `WEAVE_PRINT_CALL_LINK` | `true` | UI リンク出力 |
| `WEAVE_PARALLELISM` | `20` | 評価時の並列数 |

**3. 依存関係をインストール**

**uv を使う場合（推奨）:**

```bash
uv sync
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

**pip を使う場合:**

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**4. スクリプトを実行**

仮想環境を有効化していれば、`uv` を付けずに実行できます。

```bash
python jp/1_1_basic_trace.py
```

以下のメッセージが表示されれば成功です:

```text
============================================================
Basic Trace Demo Complete!
============================================================
```

このメッセージが表示されない場合は、エラーメッセージを確認して環境変数や依存関係を見直してください。

## リソース

- **ドキュメント**: [W&B Weave Documentation](https://docs.wandb.ai/weave)
- **日本語キャッチアップ資料**: [W&B Models / Weave](https://note.com/wandb_jp/n/n94100f3961fc)
- **W&B Skills**: [wandb/skills](https://github.com/wandb/skills)
- **W&B MCP Server**: [MCP Server Documentation](https://docs.wandb.ai/platform/mcp-server)
- **Agent 向け Trace**: [Trace agents](https://docs.wandb.ai/weave/guides/tracking/trace-agents)
- **Built-in Scorers**: [Built-in Scorers](https://docs.wandb.ai/weave/guides/evaluation/builtin_scorers)
- **Automations**: [Set up automations](https://docs.wandb.ai/weave/guides/evaluation/automations)
- **Dynamic Leaderboards**: [Create dynamic Leaderboards](https://docs.wandb.ai/weave/guides/evaluation/dynamic_leaderboards)
- **Trace Plots**: [Use trace plots](https://docs.wandb.ai/weave/guides/tracking/trace-plots)
- **Saved Views**: [Create and manage saved views](https://docs.wandb.ai/weave/guides/tools/saved-views)
- **環境変数**: [Environment Variables](https://docs.wandb.ai/weave/guides/core-types/env-vars)
- **動画**:
  - [日本語チュートリアル](https://www.youtube.com/watch?v=Ua0Wx9fqhDo&t=295s)
  - [英語チュートリアル](https://www.youtube.com/watch?v=sJNjw6U2Tvg&t=522s)
