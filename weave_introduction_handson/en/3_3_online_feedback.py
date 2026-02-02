"""
3_3: Online Feedback

What you'll learn in this script:
================================
1. Adding feedback to traces
2. Reactions, notes, and custom feedback
3. Using feedback

Feedback Use Cases:
- Tracking user satisfaction
- Marking problematic responses
- Sharing comments across teams
"""

import os
from dotenv import load_dotenv
import weave

from config_loader import chat_completion

# Load environment variables
load_dotenv()

# Initialize Weave
# Initialize with weave.init("entity/project")
client_weave = weave.init(f"{os.getenv('WANDB_ENTITY')}/{os.getenv('WANDB_PROJECT', 'weave-handson')}")


# =============================================================================
# 1. Basic Feedback
# =============================================================================
print("\n" + "=" * 60)
print("1. Basic Feedback")
print("=" * 60)


@weave.op()
def generate_response(query: str) -> str:
    """Generate a response."""
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": query},
    ]
    return chat_completion(messages)


# Generate and add feedback
result, call = generate_response.call("What is the meaning of life?")
print(f"Response: {result[:80]}...")

# Add feedback
call.feedback.add_reaction("👍")
call.feedback.add_note("Thoughtful philosophical response.")
call.feedback.add("quality", {"score": 4, "reason": "Clear and well-structured"})

print(f"Added feedback to call: {call.id}")


print("\n" + "=" * 60)
print("Online Feedback Demo Complete!")
print("=" * 60)
print("\nCheck in Weave UI:")
print("- View traces with feedback in Traces tab")
print("- Filter by reactions")
