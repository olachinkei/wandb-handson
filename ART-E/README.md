# ART-E: Email Search Agent

## はじめに

**Agentic RL（エージェント強化学習）** は、LLMをツール呼び出しや複数ステップの推論が必要なタスクに特化させるための強化学習手法です。汎用モデルに対して、企業固有のタスク（メール検索、カスタマーサポート、文書要約など）を実行するエージェントとしての能力を、実際のタスク遂行を通じて学習させます。

**[ART](https://github.com/openpipe/art)** は、W&Bが買収した [OpenPipe](https://openpipe.ai) が開発した Agentic RL フレームワークです。GRPO（Group Relative Policy Optimization）とRULER（相対スコアリング）を組み合わせ、数行のコードでエージェントの強化学習を実行できます。

このハンズオンでは、**[W&B Training](https://docs.wandb.ai/ja/training)** を使用します。Serverless RL は、W&B の親会社である **CoreWeave** が提供する GPU リソース上で、インフラ構築不要で RL トレーニングを実行できるサービスです。トレーニングと推論の両方がクラウド上で実行されるため、手元に GPU がなくてもエージェントの強化学習を試すことができます。 詳しくは以下のブログ記事を参照してください：
- [W&B Training と Serverless RL](https://note.com/wandb_jp/n/n6ef91cd095f4?magazine_key=m94adeea366ce)

## 📝 ハンズオンの概要

ART-Eは、Enronメールデータセットを使用して、LLMベースのメール検索エージェントを強化学習でトレーニングするプロジェクトです。エージェントはキーワードによるメール検索、特定メールの詳細取得、ユーザーの質問に対するメールからの回答生成を行います。

ベースモデルに Qwen 3 14B を使用し、GRPO（Group Relative Policy Optimization）で強化学習、RULER（相対スコアリング手法）で評価を行います。トレーニングの記録には Weights & Biases / Weave を使用します。

## 🔧 環境構築


### GPU について 

- W&B multi-tenant SaaSをご利用の場合: このハンズオンでは Serverless Backend (GPU) を使用するため、手元に GPU は基本的に不要です。トレーニングと推論は CoreWeave のクラウド GPU 上で実行されます。

- W&B Dedicated Cloud, Onpremiseをご利用の場合: Serverless Backend (GPU) を使用できないので、GPUをご準備いただく必要があります。Qwen 3 14B モデルのトレーニングには、VRAM 80GB 以上の GPU　(NVIDIA H100 80GBやA100 80GB）が推奨となります。

### 前提条件

- Python 3.11以上
- [uv](https://docs.astral.sh/uv/) パッケージマネージャー

**uvのインストール**

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Homebrew (macOS)
brew install uv
```

### プロジェクトセットアップ

```bash
# リポジトリをクローン（またはディレクトリに移動）
cd ART-E

# 仮想環境を作成してパッケージをインストール
uv venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate  # Windows

# 依存パッケージをインストール
uv pip install -r requirements.txt

# 自前の GPU で LocalBackend を使う場合は追加で以下を実行
uv pip install -r requirements_local.txt
```

### 環境変数の設定

`.env.example` を `.env` にコピーして、環境変数を設定します。

```bash
cp .env.example .env
```

`.env` ファイルに以下の2つのAPIキーを設定してください：

- **`OPENAI_API_KEY`**: RULER評価のジャッジモデル（GPT-4.1 / o4-mini）で使用します。[OpenAI API Keys](https://platform.openai.com/api-keys) から取得できます。
- **`WANDB_API_KEY`**: トレーニング・推論・ログの記録に使用します。[W&B Authorize](https://wandb.ai/authorize) から取得できます。

Dedicated Cloud やオンプレミス環境の W&B を使用する場合は、追加で **`WANDB_BASE_URL`** にインスタンスの URL を設定してください（例: `https://wandb.your-company.com`）。SaaS版（wandb.ai）を使用する場合は設定不要です。

## 🚀 実行方法

### トレーニングの実行

初回実行時は Enron メールデータセットのダウンロードに数分かかります。データベース（`enron_emails.db`）は初回実行時に自動生成されます。

```bash
# 仮想環境をアクティベート
source .venv/bin/activate

# トレーニング実行（Serverless Backend / CoreWeave GPU を使用）
python art_e.py

# カスタムパラメータ
python art_e.py --project my-project --max-steps 100 --groups-per-step 4

# 自前の GPU を使う場合（LocalBackend）
python art_e.py --local

# LocalBackend のデータ保存先を指定
python art_e.py --local --local-path /data/art
```

デフォルトでは Serverless Backend（CoreWeave GPU）を使用します。Dedicated Cloud やオンプレミス環境など自前の GPU でトレーニングする場合は `--local` オプションを指定してください。LocalBackend はローカルマシン上で vLLM（推論）と Unsloth/torchtune（学習）を実行します。

### コマンドラインオプション

| オプション | 説明 | デフォルト |
|-----------|------|-----------|
| `--project` | Weave/W&Bプロジェクト名 | ARTE-Email-Search-Agent |
| `--max-steps` | 最大トレーニングステップ数 | 5 |
| `--groups-per-step` | ステップあたりのグループ数 | 2 |
| `--rollouts-per-group` | グループあたりのロールアウト数 | 4 |
| `--learning-rate` | 学習率 | 1e-5 |
| `--local` | ローカル GPU を使用（LocalBackend） | False |
| `--local-path` | LocalBackend のデータ保存先パス | ./.art |

### 学習したモデルを使って推論する

トレーニング後、以下のコマンドでモデルの推論・評価を実行できます：

```bash
# W&B Inference で評価（GPU不要）
python eval_model.py --artifact-path "your-entity/your-project/model-name:version"

# ローカル GPU で評価（vLLM サーバーを自動起動）
python eval_model.py --artifact-path "your-entity/your-project/model-name:version" --local
```

| オプション | 説明 | デフォルト |
|-----------|------|-----------|
| `--artifact-path` | W&Bアーティファクトパス（必須） | - |
| `--local` | ローカル GPU で vLLM サーバーを起動して評価 | False |
| `--num-scenarios` | テストするシナリオ数 | 5 |
| `--project` | Weave/W&Bプロジェクト名 | ARTE-Email-Search-Agent |
| `--seed` | 乱数シード | None |
| `--api-key` | W&B APIキー | 環境変数から取得 |

## 🤖 Advanced Topic: coding agentで次の改善の一手を試す

トレーニングや推論評価を一通り実行したら、[wandb/skills](https://github.com/wandb/skills) をインストールしたcoding agentに、W&B / Weaveのログを見ながら次の改善案を考えさせ、コード変更と再評価まで試させることができます。

```bash
npx skills add wandb/skills
export WANDB_API_KEY=<your-key>
```

おすすめの流れ:

1. `python art_e.py` でトレーニングを実行し、W&B / WeaveにRunやTraceを記録します。
2. `python eval_model.py --artifact-path "your-entity/your-project/model-name:version"` で学習済みモデルを評価します。
3. W&B UIまたはWeave UIで、報酬、失敗したシナリオ、RULERの評価、Traceの内容を確認します。
4. coding agentに「このART-EプロジェクトのW&B/Weave結果を見て、次に改善すべき一手を提案し、最小変更で試してください」と依頼します。
5. agentが提案した改善を1つ選び、プロンプト、ツール設計、報酬設計、評価シナリオなどを変更して再実行します。
6. Before/Afterの評価結果を比較し、改善が有効なら設定やREADMEに反映します。効果が薄ければTraceやScorerを見直して次の仮説を立てます。

例:

```text
このART-EプロジェクトのW&B Run、Weave Trace、評価結果を確認して、
メール検索エージェントが失敗しやすいケースを1つ特定してください。
最小限のコード変更で改善案を実装し、再評価してBefore/Afterを説明してください。
```

## 📚 参考リンク

- [W&B Training と Serverless RL](https://note.com/wandb_jp/n/n6ef91cd095f4?magazine_key=m94adeea366ce)
- [ART ドキュメント](https://art.openpipe.ai)
- [ART GitHub](https://github.com/openpipe/art)
- [RULER ドキュメント](https://art.openpipe.ai/fundamentals/ruler)
- [ART-E ブログ記事](https://openpipe.ai/blog/art-e-mail-agent)
