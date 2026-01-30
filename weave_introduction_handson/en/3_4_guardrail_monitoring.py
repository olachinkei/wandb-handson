"""
3_4: Guardrails and Monitoring

What you'll learn in this script:
================================
1. Using Scorers as guardrails
2. Real-time safety checks
3. Scorers for monitoring

Monitoring can also be configured from the UI!
- Real-time monitoring in Traces tab
- Extract conditions with filter features
- Save monitoring conditions with Saved Views
"""

import os
import json
import asyncio
import random
from dotenv import load_dotenv
import weave
from weave import Scorer

from config_loader import chat_completion

# Load environment variables
load_dotenv()

# Initialize Weave
# Initialize with weave.init("entity/project")
weave.init(f"{os.getenv('WANDB_ENTITY')}/{os.getenv('WANDB_PROJECT', 'weave-handson')}")


# =============================================================================
# 1. Toxicity Guardrail
# =============================================================================
print("\n" + "=" * 60)
print("1. Toxicity Guardrail")
print("=" * 60)


class ToxicityGuardrail(Scorer):
    """Guard against toxic content."""
    toxic_keywords: list = ["hate", "violence", "harmful"]
    
    @weave.op
    def score(self, output: str) -> dict:
        text = output if isinstance(output, str) else str(output)
        text_lower = text.lower()
        flagged = [kw for kw in self.toxic_keywords if kw in text_lower]
        return {
            "is_safe": len(flagged) == 0,
            "flagged_keywords": flagged,
        }


@weave.op()
def generate_text(prompt: str) -> str:
    """Generate text response."""
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt},
    ]
    return chat_completion(messages)


async def safe_generate(prompt: str) -> str:
    """Generate with safety guardrail."""
    result, call = generate_text.call(prompt)
    
    guardrail = ToxicityGuardrail()
    safety = await call.apply_scorer(guardrail)
    
    if not safety.result.get("is_safe", True):
        return f"Content flagged: {safety.result.get('flagged_keywords')}"
    return result


# Test
response = asyncio.run(safe_generate("What is renewable energy?"))
print(f"Response: {response[:80]}...")


# =============================================================================
# 2. Quality Monitor
# =============================================================================
print("\n" + "=" * 60)
print("2. Quality Monitor")
print("=" * 60)


class QualityMonitor(Scorer):
    """Monitor response quality."""
    min_length: int = 20
    max_length: int = 1000
    
    @weave.op
    def score(self, output: str) -> dict:
        text = output if isinstance(output, str) else str(output)
        length = len(text)
        return {
            "length": length,
            "quality_ok": self.min_length <= length <= self.max_length,
        }


async def generate_with_monitoring(prompt: str, sample_rate: float = 0.5) -> str:
    """Generate with sampled monitoring."""
    result, call = generate_text.call(prompt)
    
    # Sample monitoring (only apply to some responses)
    if random.random() < sample_rate:
        monitor = QualityMonitor()
        quality = await call.apply_scorer(monitor)
        if not quality.result.get("quality_ok"):
            print(f"  Quality alert: {quality.result}")
    
    return result


for i in range(3):
    response = asyncio.run(generate_with_monitoring(f"Tell me fact #{i+1} about space."))
    print(f"  {i+1}. {response[:60]}...")


# =============================================================================
# 3. JSON Validator
# =============================================================================
print("\n" + "=" * 60)
print("3. JSON Format Validator")
print("=" * 60)


class JSONValidator(Scorer):
    """Validate JSON format."""
    
    @weave.op
    def score(self, output: str) -> dict:
        try:
            json.loads(output)
            return {"is_valid_json": True}
        except:
            return {"is_valid_json": False}


@weave.op()
def generate_json(prompt: str) -> str:
    """Generate JSON response."""
    messages = [
        {"role": "system", "content": "Return a JSON object with 'answer' and 'confidence'."},
        {"role": "user", "content": prompt},
    ]
    return chat_completion(messages, temperature=0)


async def validate_json_output(prompt: str) -> dict:
    result, call = generate_json.call(prompt)
    validator = JSONValidator()
    validation = await call.apply_scorer(validator)
    return {"output": result, "valid": validation.result.get("is_valid_json")}


result = asyncio.run(validate_json_output("What is 2+2?"))
print(f"Valid JSON: {result['valid']}")
print(f"Output: {result['output'][:60]}...")


# =============================================================================
# 4. PII Masking Info
# =============================================================================
print("\n" + "=" * 60)
print("4. PII Masking Reference")
print("=" * 60)

print("""
About PII Masking:
====================
Weave integrates Microsoft Presidio to
automatically mask PII before sending traces.

Details: https://docs.wandb.ai/weave/guides/tracking/redact-pii

Configuration example:
  weave.init(
      "project",
      settings={
          "pii_redaction": PresidioSettings(
              enabled=True,
              entities=["EMAIL_ADDRESS", "PHONE_NUMBER"],
          )
      }
  )
""")


print("\n" + "=" * 60)
print("Guardrails and Monitoring Demo Complete!")
print("=" * 60)
print("\nCheck in Weave UI:")
print("- Traces with scores in Traces tab")
print("- Filter to extract problematic traces")
print("- Save monitoring conditions with Saved Views")
