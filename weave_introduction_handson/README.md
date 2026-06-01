# Weave Introduction Handson

W&B Weave を使った Trace、評価、モニタリングのハンズオンです。

---

## Weaveを初めて聞いたという方へ

Weave をキャッチアップするためのアセット（ドキュメント、デモ動画、チュートリアル等）は[こちらのページ](https://wandbai.notion.site/W-B-Models-Weave-22dad8882177429ba1e9f0f05e7ceac3?source=copy_link)にまとめています。

## W&Bのアカウント発行・環境構築方法

[こちらのページ](https://wandbai.notion.site/W-B-Models-Weave-22dad8882177429ba1e9f0f05e7ceac3?source=copy_link)にW&Bのアカウント発行方法・環境構築方法を記載しています。instructionに従いながら、W&Bのアカウントを発行、API keyの取得を行なってください。Enterpriseのお客様で発行方法やWANDB_BASE_URLがわからない方は、担当のW&Bエンジニアまでご連絡ください。

Enterpriseの環境の方は、Adminの方のみTeamを作成できます。Adminの方に既存のTeam名を聞いてください。または新しいTeam作成を依頼してください。W&Bの無料アカウントでのteamの作り方は下記の通りです。

### Teamとは何か？

W&BはTeam, Project, Run(W&B Models), Trace (W&B Weave)という単位で実験を管理します。同じTeamに所属しているチームメートには自動的に実験結果が共有されます。ProjectはTeamの下の階層のフォルダのような管理単位です。Enterpriseの方は、Adminの方が複数のTeamを作れ、Free planの場合は1つしか作ることができません（複数のTeamに所属することはできます）。

![teamとは](img/whatisteam.png)

### Team(entity)の作成と招待

Top pageの"Create a team to collaborate"をクリックし、teamを作成します。なお、Freeプランの場合、teamは一つしか作れません
![team作成](img/howtocreateteam.png)

参考：作成したteamのadminであれば、team memberを招待することができます
![team invite](img/howtoinviteteammember.png)


---

## このハンズオンで学べること

### 1. Tracing (トレーシング)
- `1_1` 基本的なトレーシング (@weave.op, Library Integration, エラートラッキング)
- `1_2` Agent SDK (ツール呼び出し, Threads)
- `1_3` マルチモーダル - OpenAI (画像, 音声, PDF)
- `1_4` 高度なトレーシング (Display Name, Attributes, PII Redaction, Sampling)

### 2. Asset Management (アセット管理)
- `2_1_assets` アセット管理と Scorer 作成 (Model, Prompt, Dataset, Scorer)

### 3. Evaluation (評価)
- `3_1` オフライン評価 (weave.Evaluation, 複数Scorer)
- `3_2` EvaluationLogger (柔軟なバッチ評価)

### 4. Monitoring (モニタリング)
- `4_1` オンラインフィードバック (Reaction, Note, カスタムフィードバック)
- `4_2` ガードレールとモニタリング (Scorer をガードレールとして使用)

---

## 環境構築・デモの前に確認してほしいこと

ハンズオンを始める前に、環境が正しくセットアップされているか確認してください。

### 確認手順

**1:依存関係をインストール:**

**uv を使う場合（推奨）:**
```bash
cd weave_introduction_handson
uv sync
```

**pip を使う場合:**
```bash
cd weave_introduction_handson
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**2:`.env` ファイルを作成（下記「環境変数の設定」を参照）**

**3:動作確認スクリプトを実行:**

**uv を使う場合:**
```bash
uv run python jp/1_1_basic_trace.py
```

**pip を使う場合:**
```bash
python jp/1_1_basic_trace.py
```

以下のメッセージが表示されれば成功です:
```
============================================================
Basic Trace Demo Complete!
============================================================
```

このメッセージが表示されない場合は、エラーメッセージを確認して環境変数や依存関係を見直してください。

---

---

## 環境構築

### セットアップ

**uv を使う場合（推奨）:**
```bash
cd weave_introduction_handson
uv sync
```

**pip を使う場合:**
```bash
cd weave_introduction_handson
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 環境変数の設定

`.env` ファイルを作成:

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

**注意**: Dedicated Cloud やオンプレミス環境を利用している場合は、`WANDB_BASE_URL` に自社インスタンスの URL を設定してください。

### その他の便利な環境変数

詳細: [公式ドキュメント](https://docs.wandb.ai/weave/guides/core-types/env-vars)

| 変数名 | デフォルト | 説明 |
|--------|---------|------|
| `WEAVE_DISABLED` | false | トレーシング無効化 |
| `WEAVE_PRINT_CALL_LINK` | true | UI リンク出力 |
| `WEAVE_PARALLELISM` | 20 | 評価時の並列数 |

---

## ハンズオンの構成

```
jp/
├── config_loader.py                # OpenAI 設定ローダー
├── 1_1_basic_trace.py              # 基本的なトレーシング
├── 1_2_agent_sdk.py                # Agent SDK
├── 1_3_multimodal_openai.py        # マルチモーダル - OpenAI (画像, 音声, PDF)
├── 1_4_advanced_trace.py           # 高度なトレーシング
├── 2_1_assets.py                   # アセット管理と Scorer 作成
├── 3_1_evaluation.py              # オフライン評価 (weave.Evaluation)
├── 3_2_evaluation_logger.py       # EvaluationLogger (柔軟なバッチ評価)
├── 4_1_online_feedback.py         # オンラインフィードバック
└── 4_2_guardrail_monitoring.py    # ガードレールとモニタリング

en/  # 英語版
```

---

## 実行方法

**uv を使う場合:**
```bash
uv run python jp/1_1_basic_trace.py
```

**pip を使う場合:**
```bash
python jp/1_1_basic_trace.py
```

---

## リソース

- **ドキュメント**: [W&B Weave Documentation](https://docs.wandb.ai/weave)
- **Built-in Scorers**: [Built-in Scorers](https://docs.wandb.ai/weave/guides/evaluation/builtin_scorers)
- **環境変数**: [Environment Variables](https://docs.wandb.ai/weave/guides/core-types/env-vars)
- **動画**:
  - [日本語チュートリアル](https://www.youtube.com/watch?v=Ua0Wx9fqhDo&t=295s)
  - [英語チュートリアル](https://www.youtube.com/watch?v=sJNjw6U2Tvg&t=522s)
