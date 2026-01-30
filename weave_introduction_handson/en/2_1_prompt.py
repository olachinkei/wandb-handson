"""
2_1: Prompt Management

What you'll learn in this script:
================================
1. StringPrompt - Simple string prompts
2. Parameterized Prompt - Prompts with parameters
3. MessagesPrompt - Conversation-style prompts
4. Loading prompts with weave.ref()
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

# Path to store asset references
ASSETS_FILE = Path(__file__).parent.parent / "assets.json"


def save_asset_ref(asset_type: str, name: str, ref: str):
    """Save asset reference to local file."""
    assets = json.load(open(ASSETS_FILE)) if ASSETS_FILE.exists() else {}
    assets.setdefault(asset_type, {})[name] = ref
    json.dump(assets, open(ASSETS_FILE, 'w'), indent=2)
    print(f"Saved {asset_type}/{name}: {ref}")


# =============================================================================
# 1. StringPrompt - Simple prompts
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
# 2. Parameterized Prompt
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
# 3. MessagesPrompt - Conversation style
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
# 4. Loading prompts with weave.ref()
# =============================================================================
print("\n" + "=" * 60)
print("4. Loading prompts with weave.ref()")
print("=" * 60)

# Load ref URI from assets.json
if ASSETS_FILE.exists():
    assets = json.load(open(ASSETS_FILE))
    
    # Method 1: Use URI saved in assets.json
    if "prompts" in assets and "pirate_prompt" in assets["prompts"]:
        prompt_uri = assets["prompts"]["pirate_prompt"]
        loaded_prompt = weave.ref(prompt_uri).get()
        print(f"Loaded from URI: {loaded_prompt.format()[:50]}...")
    
    # Method 2: Reference by name (latest version)
    # weave.ref("pirate_prompt:latest").get()
    
    # Method 3: Reference specific version
    # weave.ref("pirate_prompt:v1").get()

print("""
How to use weave.ref():
========================

# Load using URI
prompt = weave.ref("weave:///entity/project/object/name:version").get()

# Load by name (latest version)
prompt = weave.ref("prompt_name:latest").get()

# Load specific version
prompt = weave.ref("prompt_name:v1").get()
prompt = weave.ref("prompt_name:v2").get()

# Use the loaded prompt
messages = [{"role": "system", "content": prompt.format()}]
""")


print("\n" + "=" * 60)
print("Prompt Management Demo Complete!")
print("=" * 60)
print(f"\nRegistered prompts saved to {ASSETS_FILE}")
print("Check version history in the Objects tab in Weave UI")
