# ART-E: Email Search Agent

[ART (Agent Reinforcement Training)](https://github.com/openpipe/art) を使用して、メール検索エージェントをトレーニングするプロジェクトです。

## 📝 概要

ART-Eは、Enronメールデータセットを使用して、LLMベースのメール検索エージェントを強化学習でトレーニングします。

### 主な機能

- **メール検索**: キーワードベースのフルテキスト検索
- **メール読み取り**: 特定のメールの詳細取得
- **質問応答**: ユーザーの質問に対してメールから回答を生成

### 使用技術

- **ベースモデル**: Qwen 3 14B
- **強化学習**: GRPO (Group Relative Policy Optimization)
- **評価**: RULER (相対スコアリング手法)
- **ロギング**: Weights & Biases / Weave

## 🔧 環境構築

### 前提条件

- Python 3.12以上
- [uv](https://docs.astral.sh/uv/) パッケージマネージャー

### uvのインストール

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
```

### 環境変数の設定

`.env.example` を `.env` にコピーして、APIキーを設定します：

```bash
# .env ファイルを作成
cp .env.example .env

# .env ファイルを編集
# OpenAI API Key（RULERジャッジモデル用）
OPENAI_API_KEY=your_openai_api_key_here

# Weights & Biases API Key（推論・トレーニング・ログ用）
WANDB_API_KEY=your_wandb_api_key_here
```

**APIキーの取得先:**
- OpenAI: https://platform.openai.com/api-keys
- W&B: https://wandb.ai/authorize

## 🚀 実行方法

### トレーニングの実行

```bash
# 仮想環境をアクティベート
source .venv/bin/activate

# 本番トレーニング（推奨パラメータ）
python art_e.py

# デモモード（小さいパラメータで高速実行）
python art_e.py --demo

# カスタムパラメータ
python art_e.py --project my-project --max-steps 100 --groups-per-step 4
```

### コマンドラインオプション

| オプション | 説明 | デフォルト |
|-----------|------|-----------|
| `--demo` | デモモード（小さいパラメータ） | False |
| `--project` | Weave/W&Bプロジェクト名 | email-search-agent |
| `--max-steps` | 最大トレーニングステップ数 | 500 (本番) / 50 (デモ) |
| `--groups-per-step` | ステップあたりのグループ数 | 8 (本番) / 2 (デモ) |
| `--rollouts-per-group` | グループあたりのロールアウト数 | 8 (本番) / 4 (デモ) |
| `--learning-rate` | 学習率 | 1e-5 |

### モデルのテスト

トレーニング後、以下のコマンドでモデルをテストできます：

```bash
# 基本的なテスト（5シナリオ）
python test_model.py

# より多くのシナリオでテスト
python test_model.py --num-scenarios 20

# デモモード
python test_model.py --demo
```

### Jupyter Notebookとして実行

```bash
# Jupyterをインストール（まだの場合）
uv pip install jupyter

# Jupyter Labを起動
jupyter lab

# "art_e (1).ipynb" を開いて実行
```

## 📁 ファイル構成

```
ART-E/
├── README.md           # このファイル
├── requirements.txt    # 依存パッケージ
├── .env.example        # 環境変数テンプレート
├── .env                # 環境変数（要作成）
├── config.py           # 設定管理
├── art_e.py            # メインスクリプト（トレーニング）
├── test_model.py       # モデルテスト
├── utils.py            # ユーティリティ関数
├── art_e (1).ipynb     # Jupyter Notebook版
└── enron_emails.db     # メールデータベース（自動生成）
```

## ⚙️ 設定の変更

`config.py` で各種設定を変更できます：

### 本番用設定（デフォルト）

```python
# config.py の default_config
TrainingConfig(
    groups_per_step=8,        # 各ステップでのグループ数
    num_epochs=20,            # エポック数
    rollouts_per_group=8,     # 各グループのロールアウト数
    learning_rate=1e-5,       # 学習率
    max_steps=500,            # 最大ステップ数
    validation_step_interval=10,  # バリデーション間隔
)

DatasetConfig(
    train_limit=500,          # トレーニングシナリオ数
    val_limit=100,            # バリデーションシナリオ数
)
```

### デモ用設定（高速テスト用）

```python
# config.py の demo_config
TrainingConfig(
    groups_per_step=2,
    num_epochs=20,
    rollouts_per_group=4,
    learning_rate=1e-5,
    max_steps=50,
    validation_step_interval=5,
)

DatasetConfig(
    train_limit=50,
    val_limit=20,
)
```

## 🔍 コード構成

### config.py

設定管理を担当：

- `ModelConfig`: モデル設定（名前、プロジェクト、ベースモデル）
- `TrainingConfig`: トレーニング設定（学習率、ステップ数など）
- `DatasetConfig`: データセット設定（シナリオ数など）
- `RulerConfig`: RULER評価設定（ジャッジモデルなど）

### utils.py

データモデルとデータベース操作を担当：

- **データモデル**
  - `Email`: メールデータ
  - `Scenario`: トレーニング/テストシナリオ
  - `SearchResult`: 検索結果
  - `FinalAnswer`: 最終回答

- **データベース関数**
  - `create_email_database()`: Enronデータセットからデータベース作成
  - `search_emails()`: メール検索
  - `read_email()`: メール読み取り
  - `load_scenarios()`: シナリオ読み込み

### art_e.py

トレーニングを担当：

- **RULER評価**
  - `judge_correctness()`: 回答正確性の評価

- **エージェント実行**
  - `ProjectTrajectory`: 実行軌跡
  - `rollout()`: エージェントのロールアウト

- **トレーニング**
  - `train()`: メイントレーニングループ
  - `initialize_model()`: モデル初期化

### test_model.py

モデルテストを担当：

- `test_single_scenario()`: 単一シナリオでテスト
- `test_model()`: 複数シナリオでテスト

## 🎯 エージェントのツール

エージェントは以下の3つのツールを使用できます：

| ツール名 | 説明 |
|---------|------|
| `search_inbox` | キーワードでメールを検索 |
| `read_email` | 特定のメールIDから詳細を取得 |
| `return_final_answer` | 最終回答とソースメールIDを返却 |

## 📊 RULER評価について

RULERは相対スコアリング手法で、以下の特徴があります：

1. **相対評価**: 複数の回答を相互に比較
2. **GRPOとの相性**: 正規化されたスコアのみが必要
3. **効率的**: 共通プレフィックスの重複排除

## ⚠️ 注意事項

- 初回実行時、Enronメールデータセットのダウンロードに数分かかります
- データベース（`enron_emails.db`）は初回実行時に自動生成されます
- トレーニングにはGPUリソースが必要です（W&Bサーバーで実行）

## 📚 参考リンク

- [ART ドキュメント](https://art.openpipe.ai)
- [ART GitHub](https://github.com/openpipe/art)
- [RULER ドキュメント](https://art.openpipe.ai/fundamentals/ruler)
- [ART-E ブログ記事](https://openpipe.ai/blog/art-e-mail-agent)
- [Discord コミュニティ](https://discord.gg/zbBHRUpwf4)

## 📄 ライセンス

このプロジェクトはARTフレームワークに基づいています。
