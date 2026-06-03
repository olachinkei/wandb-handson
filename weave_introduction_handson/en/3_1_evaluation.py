"""
3_1: Offline Evaluation - Systematic evaluation with Evaluation

What you'll learn in this script:
================================
1. weave.Evaluation - Evaluate a dataset, model, and scorers together
2. weave.Dataset - Create an evaluation dataset
3. weave.Model - Define the model under evaluation
4. Function scorers and the weave.Scorer class
5. Custom aggregation with summarize

Where to look after running:
================================
- Evals tab: Evaluation results, per-sample scores, and aggregates
- Traces tab: model.predict calls executed during evaluation
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
# 1. Create Dataset - Create an evaluation dataset
# =============================================================================
print("\n" + "=" * 60)
print("1. Create Dataset - Create an evaluation dataset")
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
# 2. Define Model - Define the model under evaluation
# =============================================================================
print("\n" + "=" * 60)
print("2. Define Model - Define the model under evaluation")
print("=" * 60)


class GrammarCorrector(weave.Model):
    """Grammar correction model. Evaluation calls predict automatically."""

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
# 3. Define Scorers - Define evaluation functions
# =============================================================================
print("\n" + "=" * 60)
print("3. Define Scorers - Define evaluation functions")
print("=" * 60)


@weave.op()
def exact_match(expected: str, output: dict) -> dict:
    """Check whether the corrected sentence exactly matches the expected text."""
    corrected = output.get("corrected", "") if isinstance(output, dict) else str(output)
    return {"match": expected.strip() == corrected.strip()}


class SimilarityScorer(weave.Scorer):
    """Compute simple word-overlap similarity and aggregate the average."""

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
# 4. Run Evaluation - Run the evaluation
# =============================================================================
print("\n" + "=" * 60)
print("4. Run Evaluation - Run the evaluation")
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
Summary:
- Pass a Dataset, Model, and Scorers into Evaluation
- Run all samples with Evaluation.evaluate()
- Add scorer-level aggregation with summarize()

Check in Weave UI:
- Use the Evals tab to inspect evaluation results, per-sample scores, and aggregates
- Use the Traces tab to inspect model.predict calls
""")
