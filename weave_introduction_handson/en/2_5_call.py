"""
2_5: Call - Calling Assets

What you'll learn in this script:
================================
1. Referencing and retrieving saved assets
2. Calling prompts, datasets, and models
3. Pipelines combining assets

Prerequisites:
--------
Run 2_1_prompt.py, 2_2_dataset.py, 2_3_model.py first.
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv
import weave

from config_loader import chat_completion

# Load environment variables
load_dotenv()

# Initialize Weave
# Initialize with weave.init("entity/project")
weave.init(f"{os.getenv('WANDB_ENTITY')}/{os.getenv('WANDB_PROJECT', 'weave-handson')}")

# Path to asset references
ASSETS_FILE = Path(__file__).parent.parent / "assets.json"


def load_assets():
    """Load asset references from local file."""
    if ASSETS_FILE.exists():
        return json.load(open(ASSETS_FILE))
    print(f"{ASSETS_FILE} not found. Run 2_1-2_3 first.")
    return {}


# =============================================================================
# 1. Loading Assets
# =============================================================================
print("\n" + "=" * 60)
print("1. Loading Assets")
print("=" * 60)

assets = load_assets()
print("Registered assets:")
for asset_type, items in assets.items():
    if items:
        print(f"  {asset_type}: {list(items.keys())}")


# =============================================================================
# 2. Using Loaded Assets
# =============================================================================
print("\n" + "=" * 60)
print("2. Using Loaded Assets")
print("=" * 60)

# Load and use prompt
if assets.get("prompts", {}).get("pirate_prompt"):
    prompt = weave.ref(assets["prompts"]["pirate_prompt"]).get()
    messages = [
        {"role": "system", "content": prompt.format()},
        {"role": "user", "content": "What is Python?"},
    ]
    response = chat_completion(messages)
    print(f"Pirate prompt: {response[:80]}...")

# Load and use model
if assets.get("models", {}).get("qa_model"):
    model = weave.ref(assets["models"]["qa_model"]).get()
    result = model.predict("What is gravity?")
    print(f"QA model: {result['answer'][:80]}...")

# Load and use dataset
if assets.get("datasets", {}).get("qa_dataset"):
    dataset = weave.ref(assets["datasets"]["qa_dataset"]).get()
    print(f"Dataset: {len(dataset.rows)} rows")


# =============================================================================
# 3. Combined Pipeline
# =============================================================================
print("\n" + "=" * 60)
print("3. Combined Pipeline")
print("=" * 60)


@weave.op()
def run_qa_pipeline(question: str, model, scorer) -> dict:
    """Run Q&A with scoring."""
    output = model.predict(question)
    score = scorer.score(output)
    return {"question": question, "answer": output.get('answer', ''), "score": score}


if assets.get("models", {}).get("qa_model") and assets.get("scorers", {}).get("length_scorer"):
    model = weave.ref(assets["models"]["qa_model"]).get()
    scorer = weave.ref(assets["scorers"]["length_scorer"]).get()
    
    result = run_qa_pipeline("Explain machine learning briefly.", model, scorer)
    print(f"Pipeline result:")
    print(f"  Answer: {result['answer'][:60]}...")
    print(f"  Score: {result['score']}")


print("\n" + "=" * 60)
print("Call Demo Complete!")
print("=" * 60)
