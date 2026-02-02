"""
3_2: Evaluation Logger - EvaluationLoggerの活用

このスクリプトで学べること:
================================
1. EvaluationLogger の基本的な使い方
2. バッチ予測での評価
3. カスタムスコアの記録

EvaluationLogger の特徴:
- 標準の Evaluation より柔軟
- バッチ処理に対応
- 既存のパイプラインへの統合が容易
"""

import os
import json
from dotenv import load_dotenv
import weave
from weave import EvaluationLogger, Scorer

from config_loader import chat_completion

# Load environment variables
load_dotenv()

# Initialize Weave
# weave.init("entity/project") で初期化
weave.init(f"{os.getenv('WANDB_ENTITY')}/{os.getenv('WANDB_PROJECT', 'weave-handson')}")


# =============================================================================
# 1. Define Scorers (same as 3_1_offline_evaluation.py)
# =============================================================================
print("\n" + "=" * 60)
print("1. Defining Scorers")
print("=" * 60)


@weave.op()
def exact_match_scorer(expected: str, output: str) -> dict:
    """Check for exact match."""
    return {'exact_match': expected.lower() in output.lower()}


@weave.op()
def contains_answer_scorer(expected: str, output: str) -> dict:
    """Check if expected answer is contained."""
    return {'contains_answer': expected.lower() in output.lower()}


class LLMJudgeScorer(Scorer):
    """LLM as a Judge scorer."""
    
    @weave.op
    def score(self, question: str, expected: str, output: str) -> dict:
        messages = [
            {"role": "system", "content": """Evaluate response quality.
Return JSON: {"quality_score": 1-5, "is_correct": bool}"""},
            {"role": "user", "content": f"Q: {question}\nExpected: {expected}\nResponse: {output}"},
        ]
        
        try:
            return json.loads(chat_completion(messages, temperature=0))
        except:
            return {"quality_score": 0, "is_correct": False}


print("Defined: exact_match_scorer, contains_answer_scorer, LLMJudgeScorer")


# =============================================================================
# 2. Basic EvaluationLogger
# =============================================================================
print("\n" + "=" * 60)
print("2. Basic EvaluationLogger")
print("=" * 60)


@weave.op
def answer_question(question: str) -> str:
    """Answer a question."""
    messages = [
        {"role": "system", "content": "Answer concisely."},
        {"role": "user", "content": question},
    ]
    return chat_completion(messages)


# Create logger
eval_logger = EvaluationLogger(
    model="qa_model",
    dataset="qa_dataset",
    name="qa_evaluation_logger",
)

# Evaluation samples
samples = [
    {"question": "What is the capital of France?", "expected": "Paris"},
    {"question": "Who wrote 'Romeo and Juliet'?", "expected": "William Shakespeare"},
    {"question": "What is the square root of 64?", "expected": "8"},
    {"question": "What is the chemical symbol for water?", "expected": "H2O"},
    {"question": "In which year did World War II end?", "expected": "1945"},
]

print(f"Evaluating {len(samples)} samples...")

llm_judge = LLMJudgeScorer()
all_exact_match = []
all_contains_answer = []

for sample in samples:
    # Get prediction
    output = answer_question(sample["question"])
    
    # Log prediction
    pred_logger = eval_logger.log_prediction(
        inputs={"question": sample["question"]},
        output=output,
    )
    
    # Apply scorers (same as 3_1_offline_evaluation.py)
    exact_match_result = exact_match_scorer(sample["expected"], output)
    contains_result = contains_answer_scorer(sample["expected"], output)
    llm_judge_result = llm_judge.score(sample["question"], sample["expected"], output)
    
    # Log scores
    pred_logger.log_score(scorer="exact_match_scorer", score=exact_match_result)
    pred_logger.log_score(scorer="contains_answer_scorer", score=contains_result)
    pred_logger.log_score(scorer="LLMJudgeScorer", score=llm_judge_result)
    pred_logger.finish()
    
    all_exact_match.append(exact_match_result['exact_match'])
    all_contains_answer.append(contains_result['contains_answer'])
    status = "✓" if contains_result['contains_answer'] else "✗"
    print(f"  {status} {sample['question'][:30]}...")

# Log summary
exact_match_accuracy = sum(all_exact_match) / len(all_exact_match)
contains_accuracy = sum(all_contains_answer) / len(all_contains_answer)
eval_logger.log_summary({
    "exact_match_accuracy": exact_match_accuracy,
    "contains_answer_accuracy": contains_accuracy,
    "total": len(samples)
})

print(f"\nExact Match Accuracy: {exact_match_accuracy:.1%}")
print(f"Contains Answer Accuracy: {contains_accuracy:.1%}")


print("\n" + "=" * 60)
print("Evaluation Logger Demo Complete!")
print("=" * 60)
