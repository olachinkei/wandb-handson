"""
3_1: Offline Evaluation - Evaluation による系統的な評価

このスクリプトで学べること:
================================
1. weave.Evaluation - データセット・モデル・スコアラーをまとめて評価
2. weave.Dataset - 評価用データセットの作成
3. weave.Model - 評価対象モデルの定義
4. 関数スコアラーと weave.Scorer クラス
5. summarize によるカスタム集計

実行後に確認する場所:
================================
- Evals タブ: 評価結果、各サンプルのスコア、集計
- Traces タブ: 評価中に実行された model.predict
"""

import asyncio

from dotenv import load_dotenv
from openai import OpenAI
import weave
from weave import Dataset, Evaluation

from config_loader import get_model_name, init_weave

# Load environment variables
load_dotenv()

# Initialize Weave
init_weave()


# =============================================================================
# 1. Create Dataset - 評価用データセットの作成
# =============================================================================
print("\n" + "=" * 60)
print("1. Create Dataset - 評価用データセットの作成")
print("=" * 60)

dataset = Dataset(
    name="grammar_eval",
    rows=[
        {"sentence": "He no likes ice cream.", "expected": "He doesn't like ice cream."},
        {"sentence": "She goed to the store.", "expected": "She went to the store."},
        {"sentence": "They was playing outside.", "expected": "They were playing outside."},
        {"sentence": "I has a big dog.", "expected": "I have a big dog."},
        {"sentence": "We runned very fast.", "expected": "We ran very fast."},
    ],
)
weave.publish(dataset)
print(f"Created dataset: {len(dataset.rows)} rows")


# =============================================================================
# 2. Define Model - 評価対象モデルの定義
# =============================================================================
print("\n" + "=" * 60)
print("2. Define Model - 評価対象モデルの定義")
print("=" * 60)


class GrammarCorrector(weave.Model):
    """文法修正モデル。Evaluation は predict を自動的に呼び出します。"""

    model_name: str = get_model_name()

    @weave.op()
    def predict(self, sentence: str) -> dict:
        client = OpenAI()
        response = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": "Correct the grammar. Return only the corrected sentence.",
                },
                {"role": "user", "content": sentence},
            ],
            temperature=0,
        )
        return {"corrected": response.choices[0].message.content.strip()}


model = GrammarCorrector()
print(f"Created model: {model.model_name}")


# =============================================================================
# 3. Define Scorers - 評価関数の定義
# =============================================================================
print("\n" + "=" * 60)
print("3. Define Scorers - 評価関数の定義")
print("=" * 60)


@weave.op()
def exact_match(expected: str, output: dict) -> dict:
    """期待する修正文と完全一致するかをチェック。"""
    corrected = output.get("corrected", "") if isinstance(output, dict) else str(output)
    return {"match": expected.strip() == corrected.strip()}


class SimilarityScorer(weave.Scorer):
    """共通単語の割合で簡易類似度を計算し、平均値も集計する Scorer。"""

    @weave.op()
    def score(self, expected: str, output: dict) -> dict:
        corrected = output.get("corrected", "") if isinstance(output, dict) else str(output)
        expected_words = set(expected.lower().split())
        corrected_words = set(corrected.lower().split())
        similarity = len(expected_words & corrected_words) / max(len(expected_words), 1)
        return {"similarity": similarity}

    def summarize(self, score_rows: list) -> dict:
        avg = sum(row.get("similarity", 0) for row in score_rows) / max(len(score_rows), 1)
        return {"avg_similarity": avg}


print("Defined: exact_match, SimilarityScorer")


# =============================================================================
# 4. Run Evaluation - 評価の実行
# =============================================================================
print("\n" + "=" * 60)
print("4. Run Evaluation - 評価の実行")
print("=" * 60)

evaluation = Evaluation(
    name="grammar_eval_v1",
    dataset=dataset,
    scorers=[
        exact_match,
        SimilarityScorer(),
    ],
)

print("Running evaluation...")
summary = asyncio.run(evaluation.evaluate(model))

print("\nEvaluation Complete!")
print(f"Summary: {summary}")


print("\n" + "=" * 60)
print("Offline Evaluation Demo Complete!")
print("=" * 60)
print("""
まとめ:
- Dataset、Model、Scorer を Evaluation にまとめて渡す
- Evaluation.evaluate() で全サンプルを評価
- summarize() で Scorer 単位の集計を追加

Weave UI で確認:
- Evals タブで評価結果、各サンプルのスコア、集計を確認
- Traces タブで model.predict の呼び出しを確認
""")
