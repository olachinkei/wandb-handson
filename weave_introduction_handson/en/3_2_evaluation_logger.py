"""
3_2: Evaluation Logger - Using EvaluationLogger

What you'll learn in this script:
================================
1. Basic usage of EvaluationLogger
2. Evaluation with batch predictions
3. Recording custom scores

EvaluationLogger Features:
- More flexible than standard Evaluation
- Supports batch processing
- Easy integration into existing pipelines
"""

import os
from dotenv import load_dotenv
import weave
from weave import EvaluationLogger

from config_loader import chat_completion

# Load environment variables
load_dotenv()

# Initialize Weave
# Initialize with weave.init("entity/project")
weave.init(f"{os.getenv('WANDB_ENTITY')}/{os.getenv('WANDB_PROJECT', 'weave-handson')}")


# =============================================================================
# 1. Basic EvaluationLogger
# =============================================================================
print("\n" + "=" * 60)
print("1. Basic EvaluationLogger")
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
eval_logger = EvaluationLogger(model="qa_model", dataset="qa_dataset")

# Evaluation samples
samples = [
    {"question": "What is the capital of Japan?", "expected": "Tokyo"},
    {"question": "What is 2 + 2?", "expected": "4"},
    {"question": "Who wrote Hamlet?", "expected": "Shakespeare"},
]

print(f"Evaluating {len(samples)} samples...")

all_scores = []
for sample in samples:
    # Get prediction
    output = answer_question(sample["question"])
    
    # Log prediction
    pred_logger = eval_logger.log_prediction(
        inputs={"question": sample["question"]},
        output=output,
    )
    
    # Calculate and log scores
    is_correct = sample["expected"].lower() in output.lower()
    pred_logger.log_score(scorer="correctness", score=is_correct)
    pred_logger.log_score(scorer="length", score=len(output))
    pred_logger.finish()
    
    all_scores.append(is_correct)
    status = "✓" if is_correct else "✗"
    print(f"  {status} {sample['question'][:30]}...")

# Log summary
accuracy = sum(all_scores) / len(all_scores)
eval_logger.log_summary({"accuracy": accuracy, "total": len(samples)})

print(f"\nAccuracy: {accuracy:.1%}")


print("\n" + "=" * 60)
print("Evaluation Logger Demo Complete!")
print("=" * 60)
