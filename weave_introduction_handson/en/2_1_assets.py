"""
2_1: Assets and Scorers - Asset management and evaluation functions

What you'll learn in this script:
================================
1. weave.Model - Version LLM wrappers
2. weave.StringPrompt / weave.MessagesPrompt - Version prompts
3. weave.Dataset - Create and retrieve datasets
4. Scorer - Create and publish evaluation functions
5. Built-in Scorers - Use scorers provided by Weave

Where to look after running:
================================
- Models / Prompts / Datasets: Published assets
- Scorers: Evaluation functions you created
"""

import asyncio
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
import weave
from weave import Dataset, Scorer

from config_loader import chat_completion, get_model_name

# Load environment variables
load_dotenv()

# Initialize Weave
# Initialize with weave.init("entity/project")
ENTITY = os.getenv("WANDB_ENTITY")
PROJECT = os.getenv("WANDB_PROJECT", "weave-handson")
weave.init(f"{ENTITY}/{PROJECT}")

# Path to store asset references
ASSETS_FILE = Path(__file__).parent.parent / "assets.json"


def save_asset_ref(asset_type: str, name: str, ref: str):
    """Save an asset reference to a local file."""
    assets = json.load(open(ASSETS_FILE)) if ASSETS_FILE.exists() else {}
    assets.setdefault(asset_type, {})[name] = ref
    json.dump(assets, open(ASSETS_FILE, "w"), indent=2)
    print(f"Saved {asset_type}/{name}: {ref}")


# =============================================================================
# 1. weave.Model - Version an LLM wrapper
# =============================================================================
print("\n" + "=" * 60)
print("1. weave.Model - Version an LLM wrapper")
print("=" * 60)


class GrammarCorrector(weave.Model):
    """Grammar correction model.

    By inheriting from weave.Model and decorating predict with @weave.op(),
    configuration such as system_message / model_name / temperature and
    inference code can be versioned together.
    """

    system_message: str
    model_name: str
    temperature: float = 0.0

    @weave.op()
    def predict(self, sentence: str) -> dict:
        oai = OpenAI()
        response = oai.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": sentence},
            ],
            temperature=self.temperature,
        )
        return {"corrected": response.choices[0].message.content}


model_v1 = GrammarCorrector(
    system_message="You are a grammar checker. Return only the corrected sentence.",
    model_name=get_model_name(),
)
result = model_v1.predict("She goed to the store yesterday.")
print(f"v1 result: {result}")

model_v2 = GrammarCorrector(
    system_message="You are an expert grammar checker. Return only the corrected sentence, no explanation.",
    model_name=get_model_name(),
)
result = model_v2.predict("I has a big dog.")
print(f"v2 result: {result}")

model_ref = weave.publish(model_v2, name="grammar_corrector")
save_asset_ref("models", "grammar_corrector", model_ref.uri())

retrieved_model = weave.ref(model_ref.uri()).get()
print(f"Retrieved model: system_message={retrieved_model.system_message[:60]}...")


# =============================================================================
# 2. weave.StringPrompt / weave.MessagesPrompt - Prompt management
# =============================================================================
print("\n" + "=" * 60)
print("2. weave.StringPrompt / weave.MessagesPrompt - Prompt management")
print("=" * 60)

# StringPrompt - single string prompt
system_prompt = weave.StringPrompt("You speak like a friendly pirate.")
prompt_ref = weave.publish(system_prompt, name="pirate_prompt")
save_asset_ref("prompts", "pirate_prompt", prompt_ref.uri())

messages = [
    {"role": "system", "content": system_prompt.format()},
    {"role": "user", "content": "What is machine learning?"},
]
response = chat_completion(messages, max_tokens=80)
print(f"StringPrompt response: {response[:100]}...")

# MessagesPrompt - chat-message prompt template
messages_prompt = weave.MessagesPrompt(
    [
        {"role": "system", "content": "You are a helpful assistant specializing in {domain}."},
        {"role": "user", "content": "{question}"},
    ]
)
messages_prompt_ref = weave.publish(messages_prompt, name="domain_expert_prompt")
save_asset_ref("prompts", "domain_expert_prompt", messages_prompt_ref.uri())

formatted = messages_prompt.format(
    domain="machine learning",
    question="What is overfitting?",
)
response = chat_completion(formatted, max_tokens=80)
print(f"MessagesPrompt response: {response[:100]}...")

loaded_prompt = weave.ref(messages_prompt_ref.uri()).get()
print(f"Loaded prompt messages: {loaded_prompt.format(domain='AI', question='What is Weave?')}")


# =============================================================================
# 3. weave.Dataset - Create and retrieve datasets
# =============================================================================
print("\n" + "=" * 60)
print("3. weave.Dataset - Create and retrieve datasets")
print("=" * 60)

grammar_dataset = Dataset(
    name="grammar_benchmark",
    rows=[
        {"id": "0", "sentence": "He no likes ice cream.", "correction": "He doesn't like ice cream."},
        {"id": "1", "sentence": "She goed to the store.", "correction": "She went to the store."},
        {"id": "2", "sentence": "They was playing outside.", "correction": "They were playing outside."},
        {"id": "3", "sentence": "I has a big dog.", "correction": "I have a big dog."},
        {"id": "4", "sentence": "We runned very fast.", "correction": "We ran very fast."},
    ],
)
dataset_ref = weave.publish(grammar_dataset)
save_asset_ref("datasets", "grammar_benchmark", dataset_ref.uri())
print(f"Published dataset: {len(grammar_dataset.rows)} rows")


@weave.op()
def dummy_model(sentence: str) -> str:
    return sentence.upper()


_, call_1 = dummy_model.call("hello world")
_, call_2 = dummy_model.call("weave is great")
calls_dataset = Dataset.from_calls([call_1, call_2])
calls_dataset_ref = weave.publish(calls_dataset, name="calls_dataset")
save_asset_ref("datasets", "calls_dataset", calls_dataset_ref.uri())
print(f"Dataset from calls: {len(calls_dataset.rows)} rows")

retrieved_dataset = weave.ref(dataset_ref.uri()).get()
print(f"Retrieved dataset: {len(retrieved_dataset.rows)} rows")
print(f"First row: {dict(retrieved_dataset.rows[0])}")


# =============================================================================
# 4. Basic Scorer - Function-based
# =============================================================================
print("\n" + "=" * 60)
print("4. Basic Scorer - Function-based")
print("=" * 60)


@weave.op()
def exact_match_scorer(expected: str, output: dict) -> dict:
    """Check exact match, ignoring case."""
    generated = output.get("answer", "") if isinstance(output, dict) else str(output)
    return {"exact_match": expected.lower().strip() in generated.lower().strip()}


@weave.op()
def contains_answer_scorer(expected: str, output: dict) -> dict:
    """Check whether the expected answer is contained in the output."""
    generated = output.get("answer", "") if isinstance(output, dict) else str(output)
    return {"contains_answer": expected.lower() in generated.lower()}


result = exact_match_scorer("Paris", {"answer": "The capital is Paris."})
print(f"Exact match: {result}")
result = contains_answer_scorer("Paris", {"answer": "The capital is Paris."})
print(f"Contains answer: {result}")


# =============================================================================
# 5. Class-based Scorer
# =============================================================================
print("\n" + "=" * 60)
print("5. Class-based Scorer")
print("=" * 60)


class LengthScorer(Scorer):
    """Check response length."""

    min_length: int = 10
    max_length: int = 500

    @weave.op
    def score(self, output: str) -> dict:
        text = output.get("answer", "") if isinstance(output, dict) else str(output)
        length = len(text)
        return {
            "length": length,
            "is_appropriate": self.min_length <= length <= self.max_length,
        }


length_scorer = LengthScorer(min_length=20, max_length=200)
length_ref = weave.publish(length_scorer, name="length_scorer")
save_asset_ref("scorers", "length_scorer", length_ref.uri())

result = length_scorer.score({"answer": "This is a test response with some content."})
print(f"Length score: {result}")


# =============================================================================
# 6. LLM as a Judge
# =============================================================================
print("\n" + "=" * 60)
print("6. LLM as a Judge")
print("=" * 60)


class LLMJudgeScorer(Scorer):
    """Use an LLM as an evaluator."""

    criteria: str = "helpfulness"

    @weave.op
    def score(self, question: str, output: dict) -> dict:
        text = output.get("answer", "") if isinstance(output, dict) else str(output)

        messages = [
            {
                "role": "system",
                "content": f"""Evaluate the response based on {self.criteria}.
Return JSON: {{"score": 1-5, "reasoning": "brief explanation"}}""",
            },
            {"role": "user", "content": f"Question: {question}\nResponse: {text}"},
        ]

        try:
            result = json.loads(chat_completion(messages, temperature=0))
        except Exception:
            result = {"score": 0, "reasoning": "Parse error"}

        return result


judge = LLMJudgeScorer(criteria="accuracy and clarity")
judge_ref = weave.publish(judge, name="llm_judge_scorer")
save_asset_ref("scorers", "llm_judge_scorer", judge_ref.uri())

result = judge.score("What is 2+2?", {"answer": "The answer is 4."})
print(f"LLM Judge score: {result}")


# =============================================================================
# 7. Built-in Scorers - Weave-provided scorers
# =============================================================================
print("\n" + "=" * 60)
print("7. Built-in Scorers - Weave-provided scorers")
print("=" * 60)

print("""
Built-in Scorers provided by Weave:
==================================

Installation: pip install weave[scorers]

1. ValidJSONScorer - JSON format validation
2. ValidXMLScorer - XML format validation
3. HallucinationFreeScorer - Hallucination detection
4. SummarizationScorer - Summarization quality evaluation
5. OpenAIModerationScorer - Content moderation
6. EmbeddingSimilarityScorer - Embedding similarity
7. PydanticScorer - Pydantic schema validation
8. ContextEntityRecallScorer (RAGAS) - Entity recall
9. ContextRelevancyScorer (RAGAS) - Context relevancy

LLM-based scorers integrate with litellm, so you can specify
models from many providers with model_id.
""")


# =============================================================================
# 8. Using Built-in Scorers - Example
# =============================================================================
print("\n" + "=" * 60)
print("8. Using Built-in Scorers - Example")
print("=" * 60)

try:
    from weave.scorers import HallucinationFreeScorer, ValidJSONScorer

    json_scorer = ValidJSONScorer()

    @weave.op()
    def generate_json() -> str:
        return '{"name": "test", "value": 42}'

    output, call = generate_json.call()
    result = asyncio.run(call.apply_scorer(json_scorer))
    print(f"ValidJSONScorer result: {result.result}")

    print("\nHallucinationFreeScorer:")
    print("  from weave.scorers import HallucinationFreeScorer")
    print("  scorer = HallucinationFreeScorer(model_id='openai/gpt-4o')")
    print("  # Requires a context column when used in Evaluation")

except ImportError:
    print("Built-in scorers are not installed. Run: pip install weave[scorers]")


print("\n" + "=" * 60)
print("Assets and Scorers Demo Complete!")
print("=" * 60)
print(f"\nRegistered asset references: {ASSETS_FILE}")
print("""
Summary:
- Create and publish weave.Model / Prompt / Dataset assets
- Define function-based and class-based Scorers
- Review the types and usage of Built-in Scorers

Check in Weave UI:
- Use Models / Prompts / Datasets to inspect published assets
- Use Scorers to inspect the evaluation functions you created
""")
