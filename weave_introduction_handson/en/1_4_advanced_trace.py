"""
1_4: Advanced Trace - Advanced tracing

What you'll learn in this script:
================================
1. Custom Display Name - Customize trace display names
2. Custom Cost Tracking - Define costs for custom models
3. Attributes - Attach custom metadata
4. PII Redaction - Automatically mask personal information
5. Threads - Manage conversation sessions
6. Sampling Rate - Control tracing sampling

Where to look after running:
================================
- Traces tab: display name, attributes, thread, and sampled calls
- Usage/Cost: Custom cost tracking
"""

import time
import uuid
from dataclasses import dataclass
from typing import Any
from dotenv import load_dotenv
import weave
from weave.utils import sanitize

from config_loader import chat_completion, init_weave

# Load environment variables
load_dotenv()

# Initialize Weave
client = init_weave()


# =============================================================================
# 1. Custom Display Name - Customize trace display names
# =============================================================================
print("\n" + "=" * 60)
print("1. Custom Display Name - Customize trace display names")
print("=" * 60)


# Method 1: Set display name with the name parameter.
@weave.op(name="sentiment_analyzer")
def analyze_sentiment(text: str) -> str:
    """Customize the name displayed in Weave UI with the name parameter.

    The function name is analyze_sentiment, but the UI displays sentiment_analyzer.
    """
    messages = [
        {"role": "system", "content": "Analyze sentiment. Return: positive/negative/neutral"},
        {"role": "user", "content": text},
    ]
    return chat_completion(messages)


result = analyze_sentiment("I love this product!")
print(f"Sentiment: {result[:30]}...")
time.sleep(2)  # Wait before next API call

# =============================================================================
# 2. Custom Cost Tracking - Define costs for custom models
# =============================================================================
print("\n" + "=" * 60)
print("2. Custom Cost Tracking - Define costs for custom models")
print("=" * 60)


CUSTOM_MODEL_ID = "my-custom-model-v1"


def register_custom_cost() -> None:
    """Register token costs for a custom model in Weave.

    prompt_token_cost / completion_token_cost are USD per token.
    For example, $2 / $6 per 1M tokens becomes 0.000002 / 0.000006.
    """
    existing_costs = client.query_costs(llm_ids=[CUSTOM_MODEL_ID])
    if existing_costs:
        print(f"Custom cost already registered: {CUSTOM_MODEL_ID}")
        return

    client.add_cost(
        llm_id=CUSTOM_MODEL_ID,
        prompt_token_cost=0.000002,
        completion_token_cost=0.000006,
    )
    print(f"Custom cost registered: {CUSTOM_MODEL_ID}")


register_custom_cost()


# =============================================================================
# 3. Attributes - Attach custom metadata
# =============================================================================
print("\n" + "=" * 60)
print("3. Attributes - Attach custom metadata")
print("=" * 60)


@weave.op()
def process_request(text: str) -> str:
    """This call is traced together with metadata attached through attributes."""
    messages = [
        {"role": "system", "content": "Summarize briefly."},
        {"role": "user", "content": text},
    ]
    return chat_completion(messages)


# Attach attributes with a context manager.
with weave.attributes({
    "environment": "development",
    "user_id": "user_123",
    "experiment_id": "exp_001",
    "model_version": "v1.2.3",
}):
    result = process_request("This is a test message.")
    print(f"Result: {result[:60]}...")


# =============================================================================
# 4. PII Redaction - Automatically mask personal information
# =============================================================================
print("\n" + "=" * 60)
print("4. PII Redaction - Automatically mask personal information")
print("=" * 60)

print("""
PII Redaction configuration:
============================

Method 1: Enable it in weave.init (using Microsoft Presidio)
-----------------------------------------------------------
pip install presidio-analyzer presidio-anonymizer

weave.init(
    "entity/project",
    settings={
        "redact_pii": True,  # Auto-detect and mask PII
        "redact_pii_fields": ["EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD"]
    }
)

Entities masked by default:
- CREDIT_CARD, EMAIL_ADDRESS, PHONE_NUMBER
- PERSON, LOCATION, IP_ADDRESS
- US_SSN, US_PASSPORT, US_DRIVER_LICENSE, etc.
""")


# Method 2: Custom masking with postprocess_inputs / postprocess_output.
@dataclass
class UserData:
    name: str
    email: str
    message: str


def redact_inputs(inputs: dict[str, Any]) -> dict[str, Any]:
    """Mask sensitive information from inputs."""
    redacted = inputs.copy()
    if "email" in redacted:
        redacted["email"] = "***@***.***"
    if "password" in redacted:
        redacted["password"] = "REDACTED"
    return redacted


def redact_output(output: UserData) -> UserData:
    """Mask sensitive information from outputs."""
    return UserData(
        name=output.name[:1] + "***",  # Keep only the first character.
        email="***@***.***",
        message=output.message,
    )


@weave.op(
    postprocess_inputs=redact_inputs,
    postprocess_output=redact_output,
)
def process_user_data(name: str, email: str, password: str) -> UserData:
    """Mask sensitive information with postprocess_inputs/output.

    The original data is used for the actual work, but Weave logs the masked data.
    """
    return UserData(
        name=name,
        email=email,
        message=f"Hello {name}, your account is ready!",
    )


result = process_user_data(
    name="John Doe",
    email="john.doe@example.com",
    password="secret123",
)
print(f"Result (actual): {result}")


# Method 3: Mask custom keys with REDACT_KEYS.
print("\n--- Method 3: REDACT_KEYS ---")
print("""
Automatically mask values with specific key names:

from weave.utils import sanitize

# Add custom keys
sanitize.add_redact_key("api_key")
sanitize.add_redact_key("secret_token")

Keys masked by default:
- api_key
- auth_headers
- authorization
""")


sanitize.add_redact_key("secret_token")


@weave.op()
def call_internal_service(payload: dict[str, Any]) -> dict[str, Any]:
    """Sample used to verify key-name-based automatic masking.

    payload["api_key"] is masked by default, and payload["secret_token"] is
    masked after adding it with add_redact_key.
    """
    return {
        "status": "ok",
        "user_id": payload["user_id"],
        "used_secret_token_suffix": payload["secret_token"][-4:],
    }


redact_keys_result = call_internal_service({
    "user_id": "user_123",
    "api_key": "sk-demo-api-key-1234567890",
    "secret_token": "internal-secret-token-abcdef",
    "request": "Create a summary for this user.",
})
print(f"Added secret_token to REDACT_KEYS: {sanitize.should_redact('secret_token')}")
print(f"Result: {redact_keys_result}")
print("Check the Weave UI Inputs to confirm api_key and secret_token are shown as REDACTED.")


# =============================================================================
# 5. Threads - Conversation session management
# =============================================================================
print("\n" + "=" * 60)
print("5. Threads - Conversation session management")
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
# 6. Sampling Rate - Sampling control
# =============================================================================
print("\n" + "=" * 60)
print("6. Sampling Rate - Sampling control")
print("=" * 60)


@weave.op(tracing_sample_rate=0.1)  # Trace only 10%.
def high_frequency_validation(data: str) -> bool:
    """High-frequency function. Only 10% of calls are traced.

    tracing_sample_rate:
    - 0.0: Do not trace
    - 0.1: Trace 10%
    - 1.0: Trace all calls (default)
    """
    return len(data) > 0


@weave.op()
def process_batch(items: list) -> dict:
    """Batch processing. Internal validation is traced only 10% of the time."""
    valid = sum(1 for item in items if high_frequency_validation(item))
    return {"total": len(items), "valid": valid}


result = process_batch(["a", "bb", "ccc", "dddd", "eeeee"])
print(f"Batch result: {result}")


print("\n" + "=" * 60)
print("Advanced Trace Demo Complete!")
print("=" * 60)
print("""
Summary:
- name: Customize display names
- custom cost: Register custom model costs
- attributes: Attach metadata
- redact_pii: Automatically mask personal information
- postprocess: Apply custom masking
- thread: Group conversation turns
- tracing_sample_rate: Control sampling

Check in Weave UI:
- Use the Traces tab to inspect display names, attributes, and threads
- Use Inputs/Outputs to inspect masked values
- Use Usage/Cost to inspect custom cost tracking
""")
