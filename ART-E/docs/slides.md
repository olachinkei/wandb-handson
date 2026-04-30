---
marp: true
theme: default
paginate: true
header: "ART-E: Email Search Agent"
footer: "Agentic RL Hands-on"
---

# ART-E: Email Search Agent

**Agentic RL でメール検索エージェントをトレーニングする**

- ART (Agent Reinforcement Training) + Serverless RL
- GRPO + RULER による強化学習
- Weights & Biases / Weave でログ記録

---

# 全体像

```
art_e.py の処理フロー
═══════════════════════════════════════════════

 1. 設定読み込み（config.py + 環境変数 + CLI引数）
 2. Weave 初期化（ログ記録の準備）
 3. モデル初期化（ART TrainableModel + Backend 登録）
 4. シナリオ読み込み（Enron メールデータセット）
 5. トレーニングループ
    ├── Rollout（エージェント実行）
    ├── RULER スコアリング（LLM ジャッジ評価）
    ├── バリデーション（定期実行）
    └── GRPO でモデル更新
```

---

# コード構成マップ

```
art_e.py
├── データモデル定義
│   ├── CorrectnessJudgeResponse   # RULER 判定結果
│   ├── ProjectTrajectory          # 実行軌跡
│   └── EmailScenario              # シナリオラッパー
│
├── RULER 評価
│   └── judge_correctness()        # LLM ジャッジで正誤判定
│
├── エージェント実行
│   └── rollout()                  # 1エピソードの実行
│
├── モデル初期化
│   ├── _register_model_with_retry()
│   └── initialize_model()         # Backend 選択 + 登録
│
├── トレーニング
│   └── train()                    # メインループ
│
└── CLI
    ├── parse_args()
    └── main()
```

---

# データモデル定義

## CorrectnessJudgeResponse

RULER の LLM ジャッジが返す構造化レスポンス

```python
class CorrectnessJudgeResponse(BaseModel):
    reasoning: str   # 判断の理由
    accept: bool     # 正解かどうか
```

---

# データモデル定義

## ProjectTrajectory

ART の `Trajectory` を拡張。1回のエージェント実行の軌跡を保持する。

```python
class ProjectTrajectory(art.Trajectory):
    final_answer: FinalAnswer | None = None
```

`Trajectory` が持つもの:
- `messages_and_choices`: メッセージ履歴
- `reward`: 報酬
- `metrics`: メトリクス（`correct` など）
- `tools`: ツール定義

---

# データモデル定義

## EmailScenario

`rollout()` に渡すためのラッパー。シナリオ + 現在のステップ番号。

```python
class EmailScenario(BaseModel):
    step: int
    scenario: Scenario  # utils.py で定義
```

`Scenario` には質問、期待される回答、メールボックス情報などが入る。

---

# RULER 評価: judge_correctness()

エージェントの回答が正しいかを **LLM ジャッジ** で判定する。

```python
@weave.op
@retry(stop=stop_after_attempt(3))
async def judge_correctness(scenario, answer) -> CorrectnessJudgeResponse:
```

**流れ:**
1. システムプロンプトで「参照回答と比較して判定せよ」と指示
2. `question` + `reference answer` + `AI answer` を渡す
3. ジャッジモデル（GPT-4.1）が `accept: true/false` を返す

- `@weave.op` でトレースを記録
- `@retry` で最大3回リトライ

---

# Rollout: エージェント実行

`rollout()` は **1エピソードのエージェント実行** を行う。

```python
@weave.op
async def rollout(model, email_scenario) -> ProjectTrajectory:
```

---

# Rollout: 処理フロー

```
 ┌─────────────────────────────────────────┐
 │  システムプロンプト設定                    │
 │  「あなたはメール検索エージェントです...」   │
 └────────────────┬────────────────────────┘
                  ▼
 ┌─────────────── ループ (最大 max_turns) ──┐
 │                                          │
 │  モデルに推論リクエスト                    │
 │          ▼                               │
 │  ツール呼び出しあり？                      │
 │    No → 終了                             │
 │    Yes ↓                                 │
 │  ツール実行                               │
 │    search_inbox / read_email              │
 │    / return_final_answer                  │
 │          ▼                               │
 │  return_final_answer なら                  │
 │    → RULER 評価して終了                   │
 │                                          │
 └──────────────────────────────────────────┘
```

---

# Rollout: 3つのツール

エージェントが使えるツール:

| ツール | 役割 |
|--------|------|
| `search_inbox(keywords)` | キーワードでメール検索 |
| `read_email(message_id)` | 特定メールの詳細取得 |
| `return_final_answer(answer, ids)` | 最終回答を返す |

ツールは **LangChain の `convert_to_openai_tool`** で OpenAI Tool 形式に変換される。

---

# モデル初期化: initialize_model()

```python
async def initialize_model(config) -> art.TrainableModel:
```

**処理:**
1. `art.TrainableModel` を宣言（名前、プロジェクト、ベースモデル）
2. Backend を選択
   - デフォルト: `ServerlessBackend()`（CoreWeave GPU）
   - `--local` 指定時: `LocalBackend(path=...)`（ローカル GPU）
3. `model.register(backend)` でバックエンドに登録（リトライ付き）

---

# トレーニングループ: train()

```python
async def train(config):
```

全体の流れを制御するメイン関数。

---

# トレーニングループ: 処理フロー

```
 Weave 初期化
     ▼
 モデル初期化
     ▼
 シナリオ読み込み（train / validation）
     ▼
 ┌── ステップごとのループ ──────────────────┐
 │                                          │
 │  1. TrajectoryGroup 作成                  │
 │     各シナリオ × rollouts_per_group 回     │
 │                                          │
 │  2. Rollout 収集                          │
 │     gather_trajectory_groups()            │
 │                                          │
 │  3. RULER スコアリング                     │
 │     ruler_score_group() で相対スコア付与   │
 │                                          │
 │  4. バリデーション（N ステップごと）        │
 │                                          │
 │  5. GRPO でモデル更新                      │
 │     model.train(judged_groups)            │
 │                                          │
 └──────────────────────────────────────────┘
```

---

# GRPO + RULER の仕組み

**GRPO (Group Relative Policy Optimization):**
- 同じシナリオに対して複数回ロールアウト
- グループ内の相対的な良さで学習（絶対スコア不要）

**RULER:**
- LLM ジャッジが各軌跡を相互比較
- 正規化された相対スコアを GRPO に渡す

```
  シナリオ A に対して 8 回ロールアウト
     ↓
  [回答1, 回答2, ..., 回答8]
     ↓
  RULER で相互比較 → 相対スコア
     ↓
  GRPO で「良い回答を出す方向」に学習
```

---

# CLI: コマンドライン引数

```bash
# Serverless Backend（デフォルト）
python art_e.py

# ローカル GPU
python art_e.py --local

# カスタムパラメータ
python art_e.py --project my-project --max-steps 100
```

| オプション | 説明 |
|-----------|------|
| `--project` | W&B プロジェクト名 |
| `--max-steps` | 最大ステップ数 |
| `--groups-per-step` | ステップあたりのグループ数 |
| `--rollouts-per-group` | グループあたりのロールアウト数 |
| `--learning-rate` | 学習率 |
| `--local` | ローカル GPU を使用 |
| `--local-path` | LocalBackend の保存先 |

---

# 設定の優先順位

```
 デフォルト値（config.py）
     ↓ 上書き
 環境変数（.env / WANDB_ENTITY, WANDB_PROJECT）
     ↓ 上書き
 コマンドライン引数（--project, --max-steps, ...）
```

`config.model.project` は `"entity/project"` 形式で統一管理。
ART に渡すときだけ `entity` と `project_name` に分割。

---

# まとめ

```
art_e.py = エージェント定義 + 評価 + トレーニングループ

  rollout()           → エージェントが 1 問を解く
  judge_correctness() → LLM が正誤を判定
  ruler_score_group() → グループ内で相対スコア
  model.train()       → GRPO でモデル更新

  これを数百ステップ繰り返す → エージェントが賢くなる
```
