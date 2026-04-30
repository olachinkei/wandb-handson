"""
3_1: Offline Evaluation - オフライン評価

このスクリプトで学べること:
================================
1. Evaluation オブジェクトの作成
2. 複数のスコアラーの適用
3. 評価結果の確認
"""

import os
import json
import asyncio
from pathlib import Path
from dotenv import load_dotenv
import weave
from weave import Evaluation, Model, Scorer

from config_loader import chat_completion, get_model_name

# Load environment variables
load_dotenv()

# Initialize Weave
# weave.init("entity/project") で初期化
weave.init(f"{os.getenv('WANDB_ENTITY')}/{os.getenv('WANDB_PROJECT', 'weave-handson')}")


# =============================================================================
# 1. Define Scorers
# =============================================================================
print("\n" + "=" * 60)
print("1. Defining Scorers")
print("=" * 60)


@weave.op()
def exact_match_scorer(expected: str, output: dict) -> dict:
    """Check for exact match."""
    generated = output.get('answer', '') if isinstance(output, dict) else str(output)
    return {'exact_match': expected.lower() in generated.lower()}


@weave.op()
def contains_answer_scorer(expected: str, output: dict) -> dict:
    """Check if expected answer is contained."""
    generated = output.get('answer', '') if isinstance(output, dict) else str(output)
    return {'contains_answer': expected.lower() in generated.lower()}


class LLMJudgeScorer(Scorer): #recommend to use Scorer to manage the scorer version
    """LLM as a Judge scorer."""
    
    @weave.op
    def score(self, question: str, expected: str, output: dict) -> dict:
        generated = output.get('answer', '') if isinstance(output, dict) else str(output)
        
        messages = [
            {"role": "system", "content": """Evaluate response quality.
Return JSON: {"quality_score": 1-5, "is_correct": bool}"""},
            {"role": "user", "content": f"Q: {question}\nExpected: {expected}\nResponse: {generated}"},
        ]
        
        try:
            return json.loads(chat_completion(messages, temperature=0))
        except:
            return {"quality_score": 0, "is_correct": False}


print("Defined: exact_match_scorer, contains_answer_scorer, LLMJudgeScorer")


# =============================================================================
# 2. Define Model
# =============================================================================
print("\n" + "=" * 60)
print("2. Defining Model")
print("=" * 60)


class QAModel(Model):
    model_name: str
    
    @weave.op()
    def predict(self, question: str) -> dict:
        messages = [
            {"role": "system", "content": "Answer concisely. Include only the answer. When writing chemical formulas, use subscript numbers like H2O, CO2."},
            {"role": "user", "content": question},
        ]
        return {"answer": chat_completion(messages, temperature=0.3)}


model = QAModel(model_name=get_model_name())
print(f"Created model: {model.model_name}")


# =============================================================================
# 3. Create Dataset
# =============================================================================
print("\n" + "=" * 60)
print("3. Creating Dataset")
print("=" * 60)

examples = [
    {"question": "What is the capital of France?", "expected": "Paris"},
    {"question": "Who wrote 'Romeo and Juliet'?", "expected": "William Shakespeare"},
    {"question": "What is the square root of 64?", "expected": "8"},
    {"question": "What is the chemical symbol for water?", "expected": "H2O"},
    {"question": "In which year did World War II end?", "expected": "1945"},
]

print(f"Created dataset with {len(examples)} examples")


# =============================================================================
# 4. Run Evaluation
# =============================================================================
print("\n" + "=" * 60)
print("4. Running Evaluation")
print("=" * 60)

evaluation = Evaluation(
    dataset=examples,
    scorers=[
        exact_match_scorer,
        contains_answer_scorer,
        LLMJudgeScorer(),
    ],
    name="qa_evaluation",
)

print("Running evaluation with 3 scorers...")
results = asyncio.run(evaluation.evaluate(model))

print("\nEvaluation Complete!")


print("\n" + "=" * 60)
print("Offline Evaluation Demo Complete!")
print("=" * 60)
