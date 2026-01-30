"""
1_3: Advanced Trace - 高度なトレーシング

このスクリプトで学べること:
================================
1. Custom Display Name - トレースの表示名をカスタマイズ
2. Kind & Color - トレースの分類と色をカスタマイズ
3. Attributes - カスタムメタデータの付与
4. PII Redaction - 個人情報の自動マスキング
5. Threads - 会話セッションの管理
6. Sampling Rate - トレーシングのサンプリング制御

実運用Tips:
----------
- 本番環境では attributes で環境情報を付与
- PII redaction で個人情報を保護
- 高頻度な呼び出しにはサンプリングを設定
"""

import os
import uuid
from dataclasses import dataclass
from typing import Any
from dotenv import load_dotenv
import weave

from config_loader import chat_completion

# Load environment variables
load_dotenv()

# Initialize Weave
# weave.init("entity/project") で初期化
weave.init(f"{os.getenv('WANDB_ENTITY')}/{os.getenv('WANDB_PROJECT', 'weave-handson')}")


# =============================================================================
# 1. Custom Display Name - トレースの表示名をカスタマイズ
# =============================================================================
print("\n" + "=" * 60)
print("1. Custom Display Name")
print("=" * 60)


# 方法1: name パラメータで表示名を設定
@weave.op(name="sentiment_analyzer")
def analyze_sentiment(text: str) -> str:
    """name パラメータで Weave UI に表示される名前をカスタマイズ。
    
    関数名は analyze_sentiment だが、UI では sentiment_analyzer と表示される。
    """
    messages = [
        {"role": "system", "content": "Analyze sentiment. Return: positive/negative/neutral"},
        {"role": "user", "content": text},
    ]
    return chat_completion(messages)


result = analyze_sentiment("I love this product!")
print(f"Sentiment: {result[:30]}...")


# =============================================================================
# 2. Kind & Color - トレースの分類と色をカスタマイズ
# =============================================================================
print("\n" + "=" * 60)
print("2. Kind & Color")
print("=" * 60)


@weave.op(kind="llm", color="blue")
def llm_call(prompt: str) -> str:
    """kind='llm' と color='blue' で LLM 呼び出しを視覚的に区別。
    
    Available kinds: agent, llm, tool, search
    Available colors: red, orange, yellow, green, blue, purple
    """
    messages = [{"role": "user", "content": prompt}]
    return chat_completion(messages)


@weave.op(kind="tool", color="green")
def search_database(query: str) -> list:
    """kind='tool' と color='green' でツール呼び出しを区別。"""
    # モックのデータベース検索
    return [{"id": 1, "title": f"Result for: {query}"}]


@weave.op(kind="agent", color="purple")
def agent_pipeline(user_query: str) -> str:
    """kind='agent' でエージェントパイプラインを表現。
    
    ネストした呼び出しで色分けを確認できます。
    """
    # ツール呼び出し
    results = search_database(user_query)
    
    # LLM 呼び出し
    context = str(results)
    response = llm_call(f"Context: {context}\nQuestion: {user_query}")
    
    return response


result = agent_pipeline("What is machine learning?")
print(f"Agent result: {result[:60]}...")


# =============================================================================
# 3. Attributes - カスタムメタデータの付与
# =============================================================================
print("\n" + "=" * 60)
print("3. Attributes - カスタムメタデータの付与")
print("=" * 60)


@weave.op()
def process_request(text: str) -> str:
    """attributes で付与されたメタデータと一緒にトレースされます。"""
    messages = [
        {"role": "system", "content": "Summarize briefly."},
        {"role": "user", "content": text},
    ]
    return chat_completion(messages)


# context manager で attributes を付与
with weave.attributes({
    "environment": "development",
    "user_id": "user_123",
    "experiment_id": "exp_001",
    "model_version": "v1.2.3",
}):
    result = process_request("This is a test message.")
    print(f"Result: {result[:60]}...")


# =============================================================================
# 4. PII Redaction - 個人情報の自動マスキング
# =============================================================================
print("\n" + "=" * 60)
print("4. PII Redaction - 個人情報の自動マスキング")
print("=" * 60)

print("""
PII Redaction の設定方法:
============================

方法1: weave.init で有効化 (Microsoft Presidio 使用)
------------------------------------------------------
pip install presidio-analyzer presidio-anonymizer

weave.init(
    "entity/project",
    settings={
        "redact_pii": True,  # PII を自動検出してマスク
        "redact_pii_fields": ["EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD"]
    }
)

デフォルトでマスクされるエンティティ:
- CREDIT_CARD, EMAIL_ADDRESS, PHONE_NUMBER
- PERSON, LOCATION, IP_ADDRESS
- US_SSN, US_PASSPORT, US_DRIVER_LICENSE など
""")


# 方法2: postprocess_inputs / postprocess_output でカスタムマスキング
@dataclass
class UserData:
    name: str
    email: str
    message: str


def redact_inputs(inputs: dict[str, Any]) -> dict[str, Any]:
    """入力から機密情報をマスク"""
    redacted = inputs.copy()
    if "email" in redacted:
        redacted["email"] = "***@***.***"
    if "password" in redacted:
        redacted["password"] = "REDACTED"
    return redacted


def redact_output(output: UserData) -> UserData:
    """出力から機密情報をマスク"""
    return UserData(
        name=output.name[:1] + "***",  # 名前の最初の文字だけ残す
        email="***@***.***",
        message=output.message,
    )


@weave.op(
    postprocess_inputs=redact_inputs,
    postprocess_output=redact_output,
)
def process_user_data(name: str, email: str, password: str) -> UserData:
    """postprocess_inputs/output で機密情報をマスク。
    
    実際の処理では元のデータを使用するが、
    Weave にログされるのはマスクされたデータ。
    """
    return UserData(
        name=name,
        email=email,
        message=f"Hello {name}, your account is ready!",
    )


# 実行
result = process_user_data(
    name="John Doe",
    email="john.doe@example.com",
    password="secret123",
)
print(f"Result (実際): {result}")


# REDACT_KEYS を使ったカスタムキーのマスク
print("\n--- REDACT_KEYS ---")
print("""
特定のキー名を持つ値を自動的にマスク:

from weave.utils import sanitize

# カスタムキーを追加
sanitize.add_redact_key("api_key")
sanitize.add_redact_key("secret_token")

デフォルトでマスクされるキー:
- api_key
- auth_headers
- authorization
""")


# =============================================================================
# 5. Threads - 会話セッション管理
# =============================================================================
print("\n" + "=" * 60)
print("5. Threads - 会話セッション管理")
print("=" * 60)


class ChatSession:
    def __init__(self):
        self.messages = []
    
    @weave.op()
    def send_message(self, user_message: str) -> str:
        self.messages.append({"role": "user", "content": user_message})
        all_messages = [{"role": "system", "content": "You are helpful."}, *self.messages]
        response = chat_completion(all_messages)
        self.messages.append({"role": "assistant", "content": response})
        return response


session = ChatSession()
session_id = str(uuid.uuid4())

with weave.thread(session_id) as thread_ctx:
    print(f"Thread ID: {thread_ctx.thread_id}")
    r1 = session.send_message("What is AI?")
    print(f"Turn 1: {r1[:60]}...")
    r2 = session.send_message("Give an example.")
    print(f"Turn 2: {r2[:60]}...")


# =============================================================================
# 6. Sampling Rate - サンプリング制御
# =============================================================================
print("\n" + "=" * 60)
print("6. Sampling Rate - サンプリング制御")
print("=" * 60)


@weave.op(tracing_sample_rate=0.1)  # 10%のみトレース
def high_frequency_validation(data: str) -> bool:
    """高頻度で呼ばれる関数。10%のみトレースされます。
    
    tracing_sample_rate:
    - 0.0: トレースしない
    - 0.1: 10% だけトレース
    - 1.0: 全てトレース (デフォルト)
    """
    return len(data) > 0


@weave.op()
def process_batch(items: list) -> dict:
    """バッチ処理。内部の validation は 10% のみトレース。"""
    valid = sum(1 for item in items if high_frequency_validation(item))
    return {"total": len(items), "valid": valid}


result = process_batch(["a", "bb", "ccc", "dddd", "eeeee"])
print(f"Batch result: {result}")


print("\n" + "=" * 60)
print("Advanced Trace Demo Complete!")
print("=" * 60)
print("""
まとめ:
- name: 表示名をカスタマイズ
- kind/color: トレースを分類・色分け
- attributes: メタデータを付与
- redact_pii: 個人情報を自動マスク
- postprocess: カスタムマスキング
- thread: 会話をグループ化
- tracing_sample_rate: サンプリング制御
""")
