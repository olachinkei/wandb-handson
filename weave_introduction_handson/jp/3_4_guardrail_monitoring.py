"""
3_4: Guardrails and Monitoring - ガードレールとモニタリング

このスクリプトで学べること:
================================
1. Scorer をガードレールとして使用
2. リアルタイムの安全性チェック
3. モニタリング用の Scorer

モニタリングは UI 上からも設定できます！
- Traces タブでリアルタイム監視
- フィルター機能で条件を抽出
- Saved Views で監視条件を保存
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
# weave.init("entity/project") で初期化
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


print("\n" + "=" * 60)
print("Guardrails and Monitoring Demo Complete!")
print("=" * 60)
