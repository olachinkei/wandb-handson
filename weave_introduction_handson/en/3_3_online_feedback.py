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


# =============================================================================
# 2. User Feedback Simulation
# =============================================================================
print("\n" + "=" * 60)
print("2. User Feedback Simulation")
print("=" * 60)


@weave.op()
def chatbot_response(message: str) -> str:
    """Customer service chatbot."""
    messages = [
        {"role": "system", "content": "You are a customer service assistant."},
        {"role": "user", "content": message},
    ]
    return chat_completion(messages)


interactions = [
    {"message": "How do I reset my password?", "helpful": True},
    {"message": "Why is my order delayed?", "helpful": False},
]

for interaction in interactions:
    response, call = chatbot_response.call(interaction["message"])
    
    # Add user feedback
    reaction = "👍" if interaction["helpful"] else "👎"
    call.feedback.add_reaction(reaction)
    call.feedback.add("helpfulness", {"helpful": interaction["helpful"]})
    
    print(f"  {reaction} {interaction['message'][:30]}...")

print("\nCheck traces with feedback in Weave UI")


# =============================================================================
# 3. Error Flagging
# =============================================================================
print("\n" + "=" * 60)
print("3. Error Flagging")
print("=" * 60)


@weave.op()
def answer_math(question: str) -> str:
    """Answer math questions."""
    messages = [
        {"role": "system", "content": "Solve the math problem."},
        {"role": "user", "content": question},
    ]
    return chat_completion(messages)


questions = [
    {"q": "What is 15 + 27?", "answer": "42"},
    {"q": "What is 100 / 8?", "answer": "12.5"},
]

for item in questions:
    result, call = answer_math.call(item["q"])
    is_correct = item["answer"] in result
    
    if is_correct:
        call.feedback.add_reaction("✅")
        call.feedback.add("verification", {"status": "correct"})
    else:
        call.feedback.add_reaction("❌")
        call.feedback.add("verification", {"status": "incorrect", "expected": item["answer"]})
    
    print(f"  {'✓' if is_correct else '✗'} {item['q']}")


print("\n" + "=" * 60)
print("Online Feedback Demo Complete!")
print("=" * 60)
print("\nCheck in Weave UI:")
print("- View traces with feedback in Traces tab")
print("- Filter by reactions")
