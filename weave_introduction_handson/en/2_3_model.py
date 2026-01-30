"""
2_3: Model Management

What you'll learn in this script:
================================
1. Creating and publishing weave.Model
2. Multiple methods (predict, invoke, generate, etc.)
3. Model parameter tracking
4. Loading models with weave.ref()
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv
import weave
from weave import Model

from config_loader import chat_completion, get_model_name

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
# 1. Creating weave.Model
# =============================================================================
print("\n" + "=" * 60)
print("1. Creating weave.Model")
print("=" * 60)


class TextAssistant(Model):
    """Text Processing Assistant
    
    By inheriting weave.Model:
    - Parameters (model_name, temperature, etc.) are automatically tracked
    - Methods with @weave.op() are automatically traced
    - Can be version-managed with publish()
    
    You can use method names other than predict!
    """
    model_name: str
    temperature: float = 0.3
    max_tokens: int = 150
    
    # ---------------------------------------------------------
    # predict: Standard prediction method
    # ---------------------------------------------------------
    @weave.op()
    def predict(self, question: str) -> dict:
        """Answer questions (standard method name)"""
        messages = [
            {"role": "system", "content": "Answer concisely."},
            {"role": "user", "content": question},
        ]
        answer = chat_completion(messages, temperature=self.temperature, max_tokens=self.max_tokens)
        return {"answer": answer, "model": self.model_name}
    
    # ---------------------------------------------------------
    # invoke: LangChain-style method name
    # ---------------------------------------------------------
    @weave.op()
    def invoke(self, prompt: str) -> str:
        """Execute a prompt (LangChain style)"""
        messages = [{"role": "user", "content": prompt}]
        return chat_completion(messages, temperature=self.temperature, max_tokens=self.max_tokens)
    
    # ---------------------------------------------------------
    # generate: For generation tasks
    # ---------------------------------------------------------
    @weave.op()
    def generate(self, topic: str, style: str = "informative") -> str:
        """Generate text about a topic"""
        messages = [
            {"role": "system", "content": f"Write in a {style} style."},
            {"role": "user", "content": f"Write about: {topic}"},
        ]
        return chat_completion(messages, temperature=0.7, max_tokens=self.max_tokens)
    
    # ---------------------------------------------------------
    # analyze: For analysis tasks
    # ---------------------------------------------------------
    @weave.op()
    def analyze(self, text: str) -> dict:
        """Analyze text"""
        messages = [
            {"role": "system", "content": "Analyze the text. Return JSON: {\"sentiment\": \"...\", \"summary\": \"...\"}"},
            {"role": "user", "content": text},
        ]
        result = chat_completion(messages, temperature=0, max_tokens=self.max_tokens)
        try:
            return json.loads(result)
        except:
            return {"raw": result}
    
    # ---------------------------------------------------------
    # translate: For translation tasks
    # ---------------------------------------------------------
    @weave.op()
    def translate(self, text: str, target_lang: str = "English") -> str:
        """Translate text"""
        messages = [
            {"role": "system", "content": f"Translate to {target_lang}. Only output the translation."},
            {"role": "user", "content": text},
        ]
        return chat_completion(messages, temperature=0.3, max_tokens=self.max_tokens)


# Create model
assistant = TextAssistant(
    model_name=get_model_name(),
    temperature=0.3,
    max_tokens=150,
)

# Publish
ref = weave.publish(assistant, name="text_assistant")
save_asset_ref("models", "text_assistant", ref.uri())


# =============================================================================
# 2. Running Each Method
# =============================================================================
print("\n" + "=" * 60)
print("2. Running Each Method")
print("=" * 60)

# predict
print("\n--- predict ---")
result = assistant.predict("What is Python?")
print(f"Answer: {result['answer'][:80]}...")

# invoke
print("\n--- invoke ---")
result = assistant.invoke("Explain AI in one sentence.")
print(f"Result: {result[:80]}...")

# generate
print("\n--- generate ---")
result = assistant.generate("machine learning", style="casual")
print(f"Generated: {result[:80]}...")

# analyze
print("\n--- analyze ---")
result = assistant.analyze("I absolutely love this new feature! It's amazing.")
print(f"Analysis: {result}")

# translate
print("\n--- translate ---")
result = assistant.translate("Hello, World!", target_lang="Japanese")
print(f"Translation: {result}")


# =============================================================================
# 3. Loading models with weave.ref()
# =============================================================================
print("\n" + "=" * 60)
print("3. Loading models with weave.ref()")
print("=" * 60)

if ASSETS_FILE.exists():
    assets = json.load(open(ASSETS_FILE))
    if "models" in assets and "text_assistant" in assets["models"]:
        # Load using URI
        model_uri = assets["models"]["text_assistant"]
        loaded = weave.ref(model_uri).get()
        
        print(f"Loaded model: {loaded.model_name}")
        print(f"  temperature: {loaded.temperature}")
        print(f"  max_tokens: {loaded.max_tokens}")
        
        # Run method on loaded model
        result = loaded.predict("What is gravity?")
        print(f"Answer: {result['answer'][:60]}...")

print("""
How to use weave.ref():
========================

# Load using URI
model = weave.ref("weave:///entity/project/object/name:version").get()

# Load by name (latest version)
model = weave.ref("text_assistant:latest").get()

# Load specific version
model = weave.ref("text_assistant:v1").get()

# Use the loaded model
result = model.predict("question")
result = model.invoke("prompt")
result = model.generate("topic")
""")


print("\n" + "=" * 60)
print("Model Management Demo Complete!")
print("=" * 60)
print(f"\nRegistered models saved to {ASSETS_FILE}")
print("Check model parameters in Weave UI")
