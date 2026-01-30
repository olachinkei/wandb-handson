"""
2_1: Prompt Management - プロンプト管理

このスクリプトで学べること:
================================
1. StringPrompt - シンプルな文字列プロンプト
2. Parameterized Prompt - パラメータ化プロンプト
3. MessagesPrompt - 会話形式のプロンプト
4. weave.ref() でプロンプトを読み込む
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
# weave.init("entity/project") で初期化
weave.init(f"{os.getenv('WANDB_ENTITY')}/{os.getenv('WANDB_PROJECT', 'weave-handson')}")

# Path to store asset references
ASSETS_FILE = Path(__file__).parent.parent / "assets.json"


def save_asset_ref(asset_type: str, name: str, ref: str):
    """Save asset reference to local file."""
    assets = json.load(open(ASSETS_FILE)) if ASSETS_FILE.exists() else {}
    assets.setdefault(asset_type, {})[name] = ref
    json.dump(assets, open(ASSETS_FILE, 'w'), indent=2)
    print(f"Saved {asset_type}/{name}: {ref}")


# =============================================================================
# 1. StringPrompt - シンプルなプロンプト
# =============================================================================
print("\n" + "=" * 60)
print("1. StringPrompt")
print("=" * 60)

# Create and publish a prompt
pirate_prompt = weave.StringPrompt("You are a pirate. Speak like a pirate.")
ref = weave.publish(pirate_prompt, name="pirate_prompt")
save_asset_ref("prompts", "pirate_prompt", ref.uri())

# Use the prompt
messages = [
    {"role": "system", "content": pirate_prompt.format()},
    {"role": "user", "content": "What is machine learning?"},
]
response = chat_completion(messages)
print(f"Pirate response: {response[:100]}...")


# =============================================================================
# 2. Parameterized Prompt - パラメータ化プロンプト
# =============================================================================
print("\n" + "=" * 60)
print("2. Parameterized Prompt")
print("=" * 60)

# Prompt with placeholder
calculator_prompt = weave.StringPrompt("Solve step by step: {equation}")
ref = weave.publish(calculator_prompt, name="calculator_prompt")
save_asset_ref("prompts", "calculator_prompt", ref.uri())

# Use with parameter
messages = [{"role": "user", "content": calculator_prompt.format(equation="2x + 5 = 15")}]
response = chat_completion(messages)
print(f"Solution: {response[:100]}...")


# =============================================================================
# 3. MessagesPrompt - 会話形式
# =============================================================================
print("\n" + "=" * 60)
print("3. MessagesPrompt")
print("=" * 60)

# Create a multi-turn prompt template
interview_prompt = weave.MessagesPrompt([
    {"role": "system", "content": "You are conducting a technical interview."},
    {"role": "user", "content": "I'm ready for my interview."},
    {"role": "assistant", "content": "Great! Tell me about a challenging project."},
    {"role": "user", "content": "{candidate_response}"},
])

ref = weave.publish(interview_prompt, name="interview_prompt")
save_asset_ref("prompts", "interview_prompt", ref.uri())

# Use MessagesPrompt
messages = interview_prompt.format(candidate_response="I built a distributed ML system.")
response = chat_completion(messages)
print(f"Interview continuation: {response[:100]}...")


# =============================================================================
# 4. weave.ref() でプロンプトを読み込む
# =============================================================================
print("\n" + "=" * 60)
print("4. weave.ref() でプロンプトを読み込む")
print("=" * 60)

# assets.json から ref URI を読み込む
if ASSETS_FILE.exists():
    assets = json.load(open(ASSETS_FILE))
    
    # 方法1: assets.json に保存した URI を使用
    if "prompts" in assets and "pirate_prompt" in assets["prompts"]:
        prompt_uri = assets["prompts"]["pirate_prompt"]
        loaded_prompt = weave.ref(prompt_uri).get()
        print(f"Loaded from URI: {loaded_prompt.format()[:50]}...")
    
    # 方法2: 名前で直接参照 (最新バージョン)
    # weave.ref("pirate_prompt:latest").get()
    
    # 方法3: 特定のバージョンを参照
    # weave.ref("pirate_prompt:v1").get()

print("""
weave.ref() の使い方:
========================

# URI を使って読み込む
prompt = weave.ref("weave:///entity/project/object/name:version").get()

# 名前で読み込む (最新バージョン)
prompt = weave.ref("prompt_name:latest").get()

# 特定のバージョンを読み込む
prompt = weave.ref("prompt_name:v1").get()
prompt = weave.ref("prompt_name:v2").get()

# 読み込んだプロンプトを使う
messages = [{"role": "system", "content": prompt.format()}]
""")


print("\n" + "=" * 60)
print("Prompt Management Demo Complete!")
print("=" * 60)
print(f"\n登録したプロンプトは {ASSETS_FILE} に保存されました")
print("Weave UI の Objects タブでバージョン履歴を確認してください")
