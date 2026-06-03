"""
3_2: EvaluationLogger - 逐次ログによる柔軟な評価

このスクリプトで学べること:
================================
1. EvaluationLogger - 推論ループ内で予測とスコアを逐次記録
2. log_prediction / log_score / finish の使い方
3. log_summary による評価全体の集計
4. 既存の推論パイプラインへの組み込み

実行後に確認する場所:
================================
- Evals タブ: 逐次ログされた予測、スコア、集計
- Traces タブ: 推論関数の call
"""

from dotenv import load_dotenv
from openai import OpenAI
import weave
from weave import EvaluationLogger

from config_loader import get_model_name, init_weave

# Load environment variables
load_dotenv()

# Initialize Weave
init_weave()


# =============================================================================
# 1. Define Prediction Function - 推論関数の定義
# =============================================================================
print("\n" + "=" * 60)
print("1. Define Prediction Function - 推論関数の定義")
print("=" * 60)


@weave.op()
def correct_grammar(sentence: str) -> dict:
    """文法を修正する推論関数。既存パイプラインに近い形で利用できます。"""
    client = OpenAI()
    response = client.chat.completions.create(
        model=get_model_name(),
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


print("Defined: correct_grammar")


# =============================================================================
# 2. Prepare EvaluationLogger - ロガーの準備
# =============================================================================
print("\n" + "=" * 60)
print("2. Prepare EvaluationLogger - ロガーの準備")
print("=" * 60)

samples = [
    {"sentence": "I has a big dog.", "expected": "I have a big dog."},
    {"sentence": "We runned very fast.", "expected": "We ran very fast."},
    {"sentence": "He are happy.", "expected": "He is happy."},
    {"sentence": "She goed to the store.", "expected": "She went to the store."},
    {"sentence": "They was playing outside.", "expected": "They were playing outside."},
]

eval_logger = EvaluationLogger(
    name="grammar_eval_logger_v1",
    model="grammar_corrector_v1",
    dataset="grammar_eval",
    scorers=["exact_match"],
)

print(f"Evaluating {len(samples)} samples...")


# =============================================================================
# 3. Log Predictions and Scores - 予測とスコアの記録
# =============================================================================
print("\n" + "=" * 60)
print("3. Log Predictions and Scores - 予測とスコアの記録")
print("=" * 60)

matches = []

for sample in samples:
    output = correct_grammar(sample["sentence"])
    corrected = output["corrected"]
    is_match = corrected == sample["expected"]

    pred_logger = eval_logger.log_prediction(
        inputs={"sentence": sample["sentence"]},
        output=output,
    )
    pred_logger.log_score("exact_match", is_match)
    pred_logger.finish()

    matches.append(is_match)
    status = "OK" if is_match else "NG"
    print(f"  {status}: {sample['sentence']} -> {corrected}")


# =============================================================================
# 4. Log Summary - 評価全体の集計
# =============================================================================
print("\n" + "=" * 60)
print("4. Log Summary - 評価全体の集計")
print("=" * 60)

accuracy = sum(matches) / len(matches)
eval_logger.log_summary(
    {
        "exact_match_accuracy": accuracy,
        "total": len(samples),
        "note": "Grammar correction samples evaluated with EvaluationLogger",
    }
)
eval_logger.finish()

print(f"Exact Match Accuracy: {accuracy:.1%}")


print("\n" + "=" * 60)
print("Evaluation Logger Demo Complete!")
print("=" * 60)
print("""
まとめ:
- EvaluationLogger で既存の推論ループを評価として記録
- log_prediction() / log_score() / finish() でサンプル単位の結果を保存
- log_summary() で評価全体の集計を保存

Weave UI で確認:
- Evals タブで逐次ログされた予測、スコア、集計を確認
- Traces タブで correct_grammar の call を確認
""")
