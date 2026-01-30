"""
1_1_0: Basic Trace - 基本的なトレーシング

このスクリプトで学べること:
================================
1. @weave.op デコレータを使った関数のトレーシング
2. LLM API の自動トラッキング (Library Integration)
3. ネストした関数呼び出しのトラッキング
4. エラートラッキング

Weave UI Tips:
--------------
- Traces タブ: すべての呼び出しを時系列で確認
- Code タブ: トラッキングしたコードを自動表示
- Inputs/Outputs: 各呼び出しの入出力を確認
"""

import os
import json
import time
from dotenv import load_dotenv
import weave

from config_loader import load_config, get_default_vendor, chat_completion

# Load environment variables
load_dotenv()

# Initialize Weave
# weave.init("entity/project") で初期化
weave.init(f"{os.getenv('WANDB_ENTITY')}/{os.getenv('WANDB_PROJECT', 'weave-handson')}")


# =============================================================================
# 1. Basic Function Tracing - 基本的な関数トレーシング
# =============================================================================
print("\n" + "=" * 60)
print("1. Basic Function Tracing")
print("=" * 60)


@weave.op()
def echo(user_input: str) -> str:
    """Simple function that echoes input twice.
    
    @weave.op() デコレータを追加するだけで、
    関数の入出力が自動的にトラッキングされます。
    """
    return user_input + " " + user_input


result = echo("hello")
print(f"Echo result: {result}")

time.sleep(2)  # 次の API 呼び出しまで待機

# =============================================================================
# 2. Library Integration - LLM API の自動トラッキング
# =============================================================================
print("\n" + "=" * 60)
print("2. Library Integration (LLM API)")
print("=" * 60)

print("""
Library Integration とは:
Weave は OpenAI、Anthropic、Gemini などの LLM ライブラリを
自動的にトラッキングします。@weave.op() デコレータなしでも
LLM API の呼び出しがトレースされます。
""")

# config.yaml の default_vendor に基づいてクライアントを選択
vendor = get_default_vendor()
print(f"使用するベンダー: {vendor} (config.yaml の default_vendor)")

if vendor == "openai":
    # =============================================
    # OpenAI の場合
    # =============================================
    import openai
    
    # OpenAI クライアントを直接使用
    # @weave.op() なしでも自動的にトレースされる
    client = openai.OpenAI()
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Tell me a short joke."},
        ],
        max_tokens=100,
    )
    
    output = response.choices[0].message.content
    print(f"OpenAI response: {output}")

elif vendor == "gemini":
    # =============================================
    # Gemini の場合
    # =============================================
    import google.generativeai as genai
    
    # Gemini クライアントを直接使用
    # @weave.op() なしでも自動的にトレースされる
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    response = model.generate_content("Tell me a short joke.")
    
    output = response.text
    print(f"Gemini response: {output}")

time.sleep(2)  # 次の API 呼び出しまで待機


# =============================================================================
# 3. Nested Function Tracing - ネストした関数呼び出し
# =============================================================================
print("\n" + "=" * 60)
print("3. Nested Function Tracing")
print("=" * 60)


@weave.op()
def create_song(user_input: str) -> str:
    """Create a song based on user input.
    
    この関数は内部で echo() と LLM API を呼び出します。
    Weave はこのネスト構造を自動的に追跡します。
    """
    echoed_input = echo(user_input)
    messages = [
        {"role": "system", "content": "Create a short song (2-3 lines) based on the input."},
        {"role": "user", "content": echoed_input},
    ]
    return chat_completion(messages, temperature=0.7)


song = create_song("sunshine")
print(f"Generated song:\n{song}")

time.sleep(2)  # 次の API 呼び出しまで待機


# =============================================================================
# 4. Error Tracking - エラートラッキング
# =============================================================================
print("\n" + "=" * 60)
print("4. Error Tracking")
print("=" * 60)


@weave.op()
def parse_json_response(user_input: str) -> dict:
    """Attempt to parse LLM response as JSON.
    
    エラーが発生した場合、Weave はエラー情報も記録します。
    ネスト構造: parse_json_response > echo > chat_completion
    """
    # echo を呼び出し（ネスト構造を作る）
    echoed = echo(user_input)
    
    messages = [
        {"role": "system", "content": "Create a song. Return as plain text."},
        {"role": "user", "content": echoed},
    ]
    response = chat_completion(messages)
    return json.loads(response)  # This may fail if response is not JSON


try:
    result = parse_json_response("hello world")
    print(f"Parsed JSON: {result}")
except json.JSONDecodeError as e:
    print(f"JSON parse error (expected): {e}")


print("\n" + "=" * 60)
print("Basic Trace Demo Complete!")
print("=" * 60)
