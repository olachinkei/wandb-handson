"""
1_1_0: Basic Trace - Fundamental Tracing

What you'll learn in this script:
================================
1. Function tracing with @weave.op decorator
2. Automatic LLM API tracking (Library Integration)
3. Nested function call tracking
4. Error tracking

Weave UI Tips:
--------------
- Traces tab: View all calls in chronological order
- Code tab: Automatically displays tracked code
- Inputs/Outputs: Check inputs and outputs for each call
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
# Initialize with weave.init("entity/project")
weave.init(f"{os.getenv('WANDB_ENTITY')}/{os.getenv('WANDB_PROJECT', 'weave-handson')}")


# =============================================================================
# 1. Basic Function Tracing
# =============================================================================
print("\n" + "=" * 60)
print("1. Basic Function Tracing")
print("=" * 60)


@weave.op()
def echo(user_input: str) -> str:
    """Simple function that echoes input twice.
    
    Just by adding the @weave.op() decorator,
    the function's inputs and outputs are automatically tracked.
    """
    return user_input + " " + user_input


result = echo("hello")
print(f"Echo result: {result}")

time.sleep(2)  # Wait before next API call

# =============================================================================
# 2. Library Integration - Automatic LLM API Tracking
# =============================================================================
print("\n" + "=" * 60)
print("2. Library Integration (LLM API)")
print("=" * 60)

print("""
What is Library Integration:
Weave automatically tracks LLM libraries like OpenAI, Anthropic, and Gemini.
LLM API calls are traced even without the @weave.op() decorator.
""")

# Select client based on default_vendor in config.yaml
vendor = get_default_vendor()
print(f"Using vendor: {vendor} (from config.yaml default_vendor)")

if vendor == "openai":
    # =============================================
    # OpenAI
    # =============================================
    import openai
    
    # Using OpenAI client directly
    # Automatically traced without @weave.op()
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
    # Gemini
    # =============================================
    import google.generativeai as genai
    
    # Using Gemini client directly
    # Automatically traced without @weave.op()
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    response = model.generate_content("Tell me a short joke.")
    
    output = response.text
    print(f"Gemini response: {output}")

time.sleep(2)  # Wait before next API call


# =============================================================================
# 3. Nested Function Tracing
# =============================================================================
print("\n" + "=" * 60)
print("3. Nested Function Tracing")
print("=" * 60)


@weave.op()
def create_song(user_input: str) -> str:
    """Create a song based on user input.
    
    This function calls echo() and LLM API internally.
    Weave automatically tracks this nested structure.
    """
    echoed_input = echo(user_input)
    messages = [
        {"role": "system", "content": "Create a short song (2-3 lines) based on the input."},
        {"role": "user", "content": echoed_input},
    ]
    return chat_completion(messages, temperature=0.7)


song = create_song("sunshine")
print(f"Generated song:\n{song}")

time.sleep(2)  # Wait before next API call


# =============================================================================
# 4. Error Tracking
# =============================================================================
print("\n" + "=" * 60)
print("4. Error Tracking")
print("=" * 60)


@weave.op()
def parse_json_response(user_input: str) -> dict:
    """Attempt to parse LLM response as JSON.
    
    When an error occurs, Weave also records the error information.
    Nested structure: parse_json_response > echo > chat_completion
    """
    # Call echo (to create nested structure)
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
