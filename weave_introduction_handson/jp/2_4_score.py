"""
2_4: Scorers - 評価関数

このスクリプトで学べること:
================================
1. 基本的な Scorer の作成
2. LLM as a Judge
3. Weave Built-in Scorers の活用

Built-in Scorers:
-----------------
Weave は以下の built-in scorer を提供しています:
- HallucinationFreeScorer: ハルシネーション検出
- SummarizationScorer: 要約品質評価
- OpenAIModerationScorer: コンテンツモデレーション
- EmbeddingSimilarityScorer: 埋め込み類似度
- ValidJSONScorer: JSON形式検証
- ValidXMLScorer: XML形式検証
- PydanticScorer: Pydanticスキーマ検証
- ContextEntityRecallScorer: エンティティリコール (RAGAS)
- ContextRelevancyScorer: コンテキスト関連性 (RAGAS)

インストール: pip install weave[scorers]
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv
import weave
from weave import Scorer

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
    print(f"Saved {asset_type}/{name}")


# =============================================================================
# 1. Basic Scorer - 関数ベース
# =============================================================================
print("\n" + "=" * 60)
print("1. Basic Scorer - Function-based")
print("=" * 60)


@weave.op()
def exact_match_scorer(expected: str, output: dict) -> dict:
    """完全一致をチェック（大文字小文字無視）"""
    generated = output.get('answer', '') if isinstance(output, dict) else str(output)
    return {'exact_match': expected.lower().strip() in generated.lower().strip()}


@weave.op()
def contains_answer_scorer(expected: str, output: dict) -> dict:
    """期待する答えが含まれているかチェック"""
    generated = output.get('answer', '') if isinstance(output, dict) else str(output)
    return {'contains_answer': expected.lower() in generated.lower()}


# Test
result = exact_match_scorer("Paris", {"answer": "The capital is Paris."})
print(f"Exact match: {result}")
result = contains_answer_scorer("Paris", {"answer": "The capital is Paris."})
print(f"Contains answer: {result}")


# =============================================================================
# 2. Class-based Scorer
# =============================================================================
print("\n" + "=" * 60)
print("2. Class-based Scorer")
print("=" * 60)


class LengthScorer(Scorer):
    """レスポンスの長さをチェック"""
    min_length: int = 10
    max_length: int = 500
    
    @weave.op
    def score(self, output: str) -> dict:
        text = output.get('answer', '') if isinstance(output, dict) else str(output)
        length = len(text)
        return {
            'length': length,
            'is_appropriate': self.min_length <= length <= self.max_length,
        }


length_scorer = LengthScorer(min_length=20, max_length=200)
ref = weave.publish(length_scorer, name="length_scorer")
save_asset_ref("scorers", "length_scorer", ref.uri())

result = length_scorer.score({"answer": "This is a test response with some content."})
print(f"Length score: {result}")


# =============================================================================
# 3. LLM as a Judge
# =============================================================================
print("\n" + "=" * 60)
print("3. LLM as a Judge")
print("=" * 60)


class LLMJudgeScorer(Scorer):
    """LLMを評価者として使用"""
    criteria: str = "helpfulness"
    
    @weave.op
    def score(self, question: str, output: dict) -> dict:
        text = output.get('answer', '') if isinstance(output, dict) else str(output)
        
        messages = [
            {"role": "system", "content": f"""Evaluate the response based on {self.criteria}.
Return JSON: {{"score": 1-5, "reasoning": "brief explanation"}}"""},
            {"role": "user", "content": f"Question: {question}\nResponse: {text}"},
        ]
        
        try:
            result = json.loads(chat_completion(messages, temperature=0))
        except:
            result = {"score": 0, "reasoning": "Parse error"}
        
        return result


judge = LLMJudgeScorer(criteria="accuracy and clarity")
ref = weave.publish(judge, name="llm_judge_scorer")
save_asset_ref("scorers", "llm_judge_scorer", ref.uri())

result = judge.score("What is 2+2?", {"answer": "The answer is 4."})
print(f"LLM Judge score: {result}")


# =============================================================================
# 4. Built-in Scorers - Weave提供のスコアラー
# =============================================================================
print("\n" + "=" * 60)
print("4. Built-in Scorers")
print("=" * 60)

print("""
Weave が提供する Built-in Scorers:
==================================

インストール: pip install weave[scorers]

1. ValidJSONScorer - JSON形式検証
   from weave.scorers import ValidJSONScorer
   scorer = ValidJSONScorer()

2. ValidXMLScorer - XML形式検証
   from weave.scorers import ValidXMLScorer
   scorer = ValidXMLScorer()

3. HallucinationFreeScorer - ハルシネーション検出
   from weave.scorers import HallucinationFreeScorer
   scorer = HallucinationFreeScorer(model_id="openai/gpt-4o")

4. SummarizationScorer - 要約品質評価
   from weave.scorers import SummarizationScorer
   scorer = SummarizationScorer(model_id="openai/gpt-4o")

5. OpenAIModerationScorer - コンテンツモデレーション
   from weave.scorers import OpenAIModerationScorer
   scorer = OpenAIModerationScorer()

6. EmbeddingSimilarityScorer - 埋め込み類似度
   from weave.scorers import EmbeddingSimilarityScorer
   scorer = EmbeddingSimilarityScorer(
       model_id="openai/text-embedding-3-small",
       threshold=0.7
   )

7. PydanticScorer - Pydanticスキーマ検証
   from weave.scorers import PydanticScorer
   from pydantic import BaseModel
   class MySchema(BaseModel):
       name: str
       value: int
   scorer = PydanticScorer(model=MySchema)

8. ContextEntityRecallScorer (RAGAS) - エンティティリコール
   from weave.scorers import ContextEntityRecallScorer
   scorer = ContextEntityRecallScorer(model_id="openai/gpt-4o")

9. ContextRelevancyScorer (RAGAS) - コンテキスト関連性
   from weave.scorers import ContextRelevancyScorer
   scorer = ContextRelevancyScorer(model_id="openai/gpt-4o")

※ LLMベースのスコアラーは litellm と統合されており、
  model_id で様々なプロバイダーのモデルを指定可能です。
""")


# =============================================================================
# 5. Using Built-in Scorers
# =============================================================================
print("\n" + "=" * 60)
print("5. Using Built-in Scorers - Example")
print("=" * 60)

try:
    from weave.scorers import ValidJSONScorer, HallucinationFreeScorer
    
    # ValidJSONScorer example
    json_scorer = ValidJSONScorer()
    
    @weave.op()
    def generate_json() -> str:
        return '{"name": "test", "value": 42}'
    
    output, call = generate_json.call()
    
    import asyncio
    result = asyncio.run(call.apply_scorer(json_scorer))
    print(f"ValidJSONScorer result: {result.result}")
    
    # HallucinationFreeScorer example
    print("\nHallucinationFreeScorer:")
    print("  from weave.scorers import HallucinationFreeScorer")
    print("  scorer = HallucinationFreeScorer(model_id='openai/gpt-4o')")
    print("  # Evaluation時に context カラムが必要")
    
except ImportError:
    print("Built-in scorers not installed. Run: pip install weave[scorers]")


print("\n" + "=" * 60)
print("Scorers Demo Complete!")
print("=" * 60)
print(f"\n登録したスコアラーは {ASSETS_FILE} に保存されました")
print("\n次のステップ:")
print("- 3_1_offline_evaluation.py で評価を実行")
print("- Built-in scorers を試す: pip install weave[scorers]")
