"""
1_3: Advanced Trace - Advanced Tracing

What you'll learn in this script:
================================
1. Custom Display Name - Customize trace display names
2. Kind & Color - Customize trace classification and colors
3. Attributes - Attach custom metadata
4. PII Redaction - Automatic masking of personal information
5. Threads - Conversation session management
6. Sampling Rate - Tracing sampling control

Production Tips:
----------
- Use attributes to attach environment info in production
- Use PII redaction to protect personal information
- Set sampling for high-frequency calls
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
# Initialize with weave.init("entity/project")
weave.init(f"{os.getenv('WANDB_ENTITY')}/{os.getenv('WANDB_PROJECT', 'weave-handson')}")


# =============================================================================
# 1. Custom Display Name
# =============================================================================
print("\n" + "=" * 60)
print("1. Custom Display Name")
print("=" * 60)


# Method 1: Set display name with name parameter
@weave.op(name="sentiment_analyzer")
def analyze_sentiment(text: str) -> str:
    """Customize the name displayed in Weave UI with name parameter.
    
    Function name is analyze_sentiment, but displayed as sentiment_analyzer in UI.
    """
    messages = [
        {"role": "system", "content": "Analyze sentiment. Return: positive/negative/neutral"},
        {"role": "user", "content": text},
    ]
    return chat_completion(messages)


result = analyze_sentiment("I love this product!")
print(f"Sentiment: {result[:30]}...")


# =============================================================================
# 2. Kind & Color - Customize trace classification and colors
# =============================================================================
print("\n" + "=" * 60)
print("2. Kind & Color")
print("=" * 60)


@weave.op(kind="llm", color="blue")
def llm_call(prompt: str) -> str:
    """Visually distinguish LLM calls with kind='llm' and color='blue'.
    
    Available kinds: agent, llm, tool, search
    Available colors: red, orange, yellow, green, blue, purple
    """
    messages = [{"role": "user", "content": prompt}]
    return chat_completion(messages)


@weave.op(kind="tool", color="green")
def search_database(query: str) -> list:
    """Distinguish tool calls with kind='tool' and color='green'."""
    # Mock database search
    return [{"id": 1, "title": f"Result for: {query}"}]


@weave.op(kind="agent", color="purple")
def agent_pipeline(user_query: str) -> str:
    """Express agent pipeline with kind='agent'.
    
    You can see color coding in nested calls.
    """
    # Tool call
    results = search_database(user_query)
    
    # LLM call
    context = str(results)
    response = llm_call(f"Context: {context}\nQuestion: {user_query}")
    
    return response


result = agent_pipeline("What is machine learning?")
print(f"Agent result: {result[:60]}...")


# =============================================================================
# 3. Attributes - Attach custom metadata
# =============================================================================
print("\n" + "=" * 60)
print("3. Attributes - Attach custom metadata")
print("=" * 60)


@weave.op()
def process_request(text: str) -> str:
    """Traced along with metadata attached via attributes."""
    messages = [
        {"role": "system", "content": "Summarize briefly."},
        {"role": "user", "content": text},
    ]
    return chat_completion(messages)


# Attach attributes with context manager
with weave.attributes({
    "environment": "development",
    "user_id": "user_123",
    "experiment_id": "exp_001",
    "model_version": "v1.2.3",
}):
    result = process_request("This is a test message.")
    print(f"Result: {result[:60]}...")


# =============================================================================
# 4. PII Redaction - Automatic masking of personal information
# =============================================================================
print("\n" + "=" * 60)
print("4. PII Redaction - Automatic masking of personal information")
print("=" * 60)

print("""
PII Redaction Configuration:
============================

Method 1: Enable in weave.init (using Microsoft Presidio)
------------------------------------------------------
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


# Method 2: Custom masking with postprocess_inputs / postprocess_output
@dataclass
class UserData:
    name: str
    email: str
    message: str


def redact_inputs(inputs: dict[str, Any]) -> dict[str, Any]:
    """Mask sensitive information from inputs"""
    redacted = inputs.copy()
    if "email" in redacted:
        redacted["email"] = "***@***.***"
    if "password" in redacted:
        redacted["password"] = "REDACTED"
    return redacted


def redact_output(output: UserData) -> UserData:
    """Mask sensitive information from output"""
    return UserData(
        name=output.name[:1] + "***",  # Keep only first character
        email="***@***.***",
        message=output.message,
    )


@weave.op(
    postprocess_inputs=redact_inputs,
    postprocess_output=redact_output,
)
def process_user_data(name: str, email: str, password: str) -> UserData:
    """Mask sensitive information with postprocess_inputs/output.
    
    Original data is used for actual processing,
    but masked data is logged to Weave.
    """
    return UserData(
        name=name,
        email=email,
        message=f"Hello {name}, your account is ready!",
    )


# Execute
result = process_user_data(
    name="John Doe",
    email="john.doe@example.com",
    password="secret123",
)
print(f"Result (actual): {result}")


# REDACT_KEYS for custom key masking
print("\n--- REDACT_KEYS ---")
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


@weave.op(tracing_sample_rate=0.1)  # Only trace 10%
def high_frequency_validation(data: str) -> bool:
    """High-frequency function. Only 10% is traced.
    
    tracing_sample_rate:
    - 0.0: No tracing
    - 0.1: Trace only 10%
    - 1.0: Trace all (default)
    """
    return len(data) > 0


@weave.op()
def process_batch(items: list) -> dict:
    """Batch processing. Internal validation is traced only 10%."""
    valid = sum(1 for item in items if high_frequency_validation(item))
    return {"total": len(items), "valid": valid}


result = process_batch(["a", "bb", "ccc", "dddd", "eeeee"])
print(f"Batch result: {result}")


print("\n" + "=" * 60)
print("Advanced Trace Demo Complete!")
print("=" * 60)
print("""
Summary:
- name: Customize display name
- kind/color: Classify and color-code traces
- attributes: Attach metadata
- redact_pii: Auto-mask personal information
- postprocess: Custom masking
- thread: Group conversations
- tracing_sample_rate: Sampling control
""")
