"""
2_1: Assets and Scorers - アセット管理と評価関数

このスクリプトで学べること:
================================
1. weave.Model - LLM ラッパーのバージョン管理
2. weave.StringPrompt / weave.MessagesPrompt - プロンプトのバージョン管理
3. weave.Dataset - データセットの作成・取得
4. Scorer - 評価関数の作成と公開
5. Built-in Scorers - Weave 提供スコアラーの使い方

実行後に確認する場所:
================================
- Models / Prompts / Datasets: 公開したアセット
- Scorers: 作成した評価関数
"""

import asyncio
import json

from dotenv import load_dotenv
from openai import OpenAI
import weave
from weave import Dataset, Scorer

from config_loader import chat_completion, get_model_name, init_weave

# Load environment variables
load_dotenv()

# Initialize Weave
init_weave()


# =============================================================================
# 1. weave.Model - LLM ラッパーのバージョン管理
# =============================================================================
print("\n" + "=" * 60)
print("1. weave.Model - LLM ラッパーのバージョン管理")
print("=" * 60)


class GrammarCorrector(weave.Model):
    """文法修正モデル。

    weave.Model を継承し、predict に @weave.op() を付けることで、
    system_message / model_name / temperature などの設定と推論コードを
    一体としてバージョン管理できます。
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
print(f"Published model: {model_ref.uri()}")

retrieved_model = weave.ref(model_ref.uri()).get()
print(f"Retrieved model: system_message={retrieved_model.system_message[:60]}...")


# =============================================================================
# 2. weave.StringPrompt / weave.MessagesPrompt - プロンプト管理
# =============================================================================
print("\n" + "=" * 60)
print("2. weave.StringPrompt / weave.MessagesPrompt - プロンプト管理")
print("=" * 60)

# StringPrompt - 単一文字列プロンプト
system_prompt = weave.StringPrompt("You speak like a friendly pirate.")
prompt_ref = weave.publish(system_prompt, name="pirate_prompt")
print(f"Published prompt: {prompt_ref.uri()}")

messages = [
    {"role": "system", "content": system_prompt.format()},
    {"role": "user", "content": "What is machine learning?"},
]
response = chat_completion(messages, max_tokens=80)
print(f"StringPrompt response: {response[:100]}...")

# MessagesPrompt - 会話履歴形式
messages_prompt = weave.MessagesPrompt(
    [
        {"role": "system", "content": "You are a helpful assistant specializing in {domain}."},
        {"role": "user", "content": "{question}"},
    ]
)
messages_prompt_ref = weave.publish(messages_prompt, name="domain_expert_prompt")
print(f"Published prompt: {messages_prompt_ref.uri()}")

formatted = messages_prompt.format(
    domain="machine learning",
    question="What is overfitting?",
)
response = chat_completion(formatted, max_tokens=80)
print(f"MessagesPrompt response: {response[:100]}...")

loaded_prompt = weave.ref(messages_prompt_ref.uri()).get()
print(f"Loaded prompt messages: {loaded_prompt.format(domain='AI', question='What is Weave?')}")


# =============================================================================
# 3. weave.Dataset - データセットの作成・取得
# =============================================================================
print("\n" + "=" * 60)
print("3. weave.Dataset - データセットの作成・取得")
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
print(f"Published dataset: {dataset_ref.uri()}")
print(f"Published dataset: {len(grammar_dataset.rows)} rows")


@weave.op()
def dummy_model(sentence: str) -> str:
    return sentence.upper()


_, call_1 = dummy_model.call("hello world")
_, call_2 = dummy_model.call("weave is great")
calls_dataset = Dataset.from_calls([call_1, call_2])
calls_dataset_ref = weave.publish(calls_dataset, name="calls_dataset")
print(f"Published dataset from calls: {calls_dataset_ref.uri()}")
print(f"Dataset from calls: {len(calls_dataset.rows)} rows")

retrieved_dataset = weave.ref(dataset_ref.uri()).get()
print(f"Retrieved dataset: {len(retrieved_dataset.rows)} rows")
print(f"First row: {dict(retrieved_dataset.rows[0])}")


# =============================================================================
# 4. Basic Scorer - 関数ベース
# =============================================================================
print("\n" + "=" * 60)
print("4. Basic Scorer - 関数ベース")
print("=" * 60)


@weave.op()
def exact_match_scorer(expected: str, output: dict) -> dict:
    """完全一致をチェック（大文字小文字無視）"""
    generated = output.get("answer", "") if isinstance(output, dict) else str(output)
    return {"exact_match": expected.lower().strip() in generated.lower().strip()}


@weave.op()
def contains_answer_scorer(expected: str, output: dict) -> dict:
    """期待する答えが含まれているかチェック"""
    generated = output.get("answer", "") if isinstance(output, dict) else str(output)
    return {"contains_answer": expected.lower() in generated.lower()}


result = exact_match_scorer("Paris", {"answer": "The capital is Paris."})
print(f"Exact match: {result}")
result = contains_answer_scorer("Paris", {"answer": "The capital is Paris."})
print(f"Contains answer: {result}")


# =============================================================================
# 5. Class-based Scorer - クラスベース
# =============================================================================
print("\n" + "=" * 60)
print("5. Class-based Scorer - クラスベース")
print("=" * 60)


class LengthScorer(Scorer):
    """レスポンスの長さをチェック"""

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
print(f"Published scorer: {length_ref.uri()}")

result = length_scorer.score({"answer": "This is a test response with some content."})
print(f"Length score: {result}")


# =============================================================================
# 6. LLM as a Judge - LLM を評価者として使う
# =============================================================================
print("\n" + "=" * 60)
print("6. LLM as a Judge - LLM を評価者として使う")
print("=" * 60)


class LLMJudgeScorer(Scorer):
    """LLMを評価者として使用"""

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
print(f"Published scorer: {judge_ref.uri()}")

result = judge.score("What is 2+2?", {"answer": "The answer is 4."})
print(f"LLM Judge score: {result}")


# =============================================================================
# 7. Built-in Scorers - Weave 提供のスコアラー
# =============================================================================
print("\n" + "=" * 60)
print("7. Built-in Scorers - Weave 提供のスコアラー")
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
# 8. Using Built-in Scorers - 実行例
# =============================================================================
print("\n" + "=" * 60)
print("8. Using Built-in Scorers - 実行例")
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
    print("  # Evaluation時に context カラムが必要")

except ImportError:
    print("Built-in scorers not installed. Run: pip install weave[scorers]")


print("\n" + "=" * 60)
print("Assets and Scorers Demo Complete!")
print("=" * 60)
print("""
まとめ:
- weave.Model / Prompt / Dataset を作成して公開
- 関数ベースとクラスベースの Scorer を定義
- Built-in Scorers の種類と使い方を確認

Weave UI で確認:
- Models / Prompts / Datasets で公開したアセットを確認
- Scorers で作成した評価関数を確認
""")
