"""
2_2: Dataset Management - データセット管理

このスクリプトで学べること:
================================
1. Dataset の作成と公開
2. データセットのバージョン管理
3. データセットの読み込みと使用
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv
import weave

# Load environment variables
load_dotenv()

# Initialize Weave
# weave.init("entity/project") で初期化
weave.init(f"{os.getenv('WANDB_ENTITY')}/{os.getenv('WANDB_PROJECT', 'weave-handson')}")

# Path to store asset references
ASSETS_FILE = Path(__file__).parent.parent / "assets.json"


def save_asset_ref(asset_type: str, name: str, ref: str):
    """Save asset reference to local file."""
    assets = json.load(open(ASSETS_FILE)) if ASSETS_FILE.exists() else {}
    assets.setdefault(asset_type, {})[name] = ref
    json.dump(assets, open(ASSETS_FILE, 'w'), indent=2)
    print(f"Saved {asset_type}/{name}")


# =============================================================================
# 1. Q&A Dataset
# =============================================================================
print("\n" + "=" * 60)
print("1. Q&A Dataset")
print("=" * 60)

qa_dataset = weave.Dataset(
    name="qa_dataset",
    rows=[
        {"question": "What is the capital of France?", "expected": "Paris"},
        {"question": "Who wrote 'Romeo and Juliet'?", "expected": "William Shakespeare"},
        {"question": "What is the square root of 64?", "expected": "8"},
        {"question": "What is the chemical symbol for water?", "expected": "H2O"},
        {"question": "In which year did World War II end?", "expected": "1945"},
    ],
)

ref = weave.publish(qa_dataset)
save_asset_ref("datasets", "qa_dataset", ref.uri())
print(f"Published dataset with {len(qa_dataset.rows)} rows")


# =============================================================================
# 2. Sentiment Dataset
# =============================================================================
print("\n" + "=" * 60)
print("2. Sentiment Dataset")
print("=" * 60)

sentiment_dataset = weave.Dataset(
    name="sentiment_analysis",
    rows=[
        {"text": "I love this product!", "expected_sentiment": "positive"},
        {"text": "This is terrible.", "expected_sentiment": "negative"},
        {"text": "It's okay, nothing special.", "expected_sentiment": "neutral"},
    ],
)

ref = weave.publish(sentiment_dataset)
save_asset_ref("datasets", "sentiment_analysis", ref.uri())
print(f"Published dataset with {len(sentiment_dataset.rows)} rows")


# =============================================================================
# 3. Loading Dataset
# =============================================================================
print("\n" + "=" * 60)
print("3. Loading Dataset")
print("=" * 60)

if ASSETS_FILE.exists():
    assets = json.load(open(ASSETS_FILE))
    if "datasets" in assets and "qa_dataset" in assets["datasets"]:
        loaded = weave.ref(assets["datasets"]["qa_dataset"]).get()
        print(f"Loaded dataset with {len(loaded.rows)} rows")
        for row in loaded.rows[:2]:
            print(f"  Q: {row['question'][:30]}... A: {row['expected']}")


print("\n" + "=" * 60)
print("Dataset Management Demo Complete!")
print("=" * 60)
print(f"\n登録したデータセットは {ASSETS_FILE} に保存されました")
print("Weave UI の Objects タブで確認してください")
