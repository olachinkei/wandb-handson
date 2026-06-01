"""
3_2: EvaluationLogger - 逐次ログによる柔軟な評価

このスクリプトで学べること:
================================
1. EvaluationLogger - 推論ループ内で予測とスコアを逐次記録
2. log_prediction / log_score / finish の使い方
3. log_summary による評価全体の集計
4. 既存の推論パイプラインへの組み込み

03_evaluations.ipynb の EvaluationLogger セクションをベースにしています。
"""

import os

from dotenv import load_dotenv
from openai import OpenAI
import weave
from weave import EvaluationLogger

from config_loader import get_model_name

# Load environment variables
load_dotenv()

# Initialize Weave
# weave.init("entity/project") で初期化
weave.init(f"{os.getenv('WANDB_ENTITY')}/{os.getenv('WANDB_PROJECT', 'weave-handson')}")


# =============================================================================
# 1. Define Prediction Function
# =============================================================================
print("\n" + "=" * 60)
print("1. Defining Prediction Function")
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
# 2. Prepare EvaluationLogger
# =============================================================================
print("\n" + "=" * 60)
print("2. Preparing EvaluationLogger")
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
# 3. Log Predictions and Scores
# =============================================================================
print("\n" + "=" * 60)
print("3. Logging Predictions and Scores")
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
# 4. Log Summary
# =============================================================================
print("\n" + "=" * 60)
print("4. Logging Summary")
print("=" * 60)

accuracy = sum(matches) / len(matches)
eval_logger.log_summary(
    {
        "exact_match_accuracy": accuracy,
        "total": len(samples),
        "note": "EvaluationLogger demo based on grammar correction samples",
    }
)
eval_logger.finish()

print(f"Exact Match Accuracy: {accuracy:.1%}")


print("\n" + "=" * 60)
print("Evaluation Logger Demo Complete!")
print("=" * 60)
print("Weave UI の Evals タブで逐次ログされた評価を確認してください。")
