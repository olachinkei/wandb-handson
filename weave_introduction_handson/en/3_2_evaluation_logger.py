"""
3_2: EvaluationLogger - Flexible evaluation with incremental logging

What you'll learn in this script:
================================
1. EvaluationLogger - Log predictions and scores inside an inference loop
2. How to use log_prediction / log_score / finish
3. Aggregate evaluation results with log_summary
4. Integrate evaluation into an existing inference pipeline

Where to look after running:
================================
- Evals tab: Incrementally logged predictions, scores, and summaries
- Traces tab: Calls from the prediction function
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
# Initialize with weave.init("entity/project")
weave.init(f"{os.getenv('WANDB_ENTITY')}/{os.getenv('WANDB_PROJECT', 'weave-handson')}")


# =============================================================================
# 1. Define Prediction Function - Define the inference function
# =============================================================================
print("\n" + "=" * 60)
print("1. Define Prediction Function - Define the inference function")
print("=" * 60)


@weave.op()
def correct_grammar(sentence: str) -> dict:
    """Grammar correction inference function for existing-pipeline style usage."""
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
# 2. Prepare EvaluationLogger - Prepare the logger
# =============================================================================
print("\n" + "=" * 60)
print("2. Prepare EvaluationLogger - Prepare the logger")
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
# 3. Log Predictions and Scores - Record predictions and scores
# =============================================================================
print("\n" + "=" * 60)
print("3. Log Predictions and Scores - Record predictions and scores")
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
# 4. Log Summary - Aggregate the full evaluation
# =============================================================================
print("\n" + "=" * 60)
print("4. Log Summary - Aggregate the full evaluation")
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
Summary:
- Use EvaluationLogger to log evaluation results from an existing inference loop
- Use log_prediction() / log_score() / finish() for each sample
- Use log_summary() to store aggregate metrics for the full evaluation

Check in Weave UI:
- Use the Evals tab to inspect incrementally logged predictions, scores, and summaries
- Use the Traces tab to inspect correct_grammar calls
""")
