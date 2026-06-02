"""
4_1: Online Feedback - Online feedback

What you'll learn in this script:
================================
1. Add feedback to traces
2. Reactions, notes, and custom feedback
3. Use feedback for review workflows

Where to look after running:
================================
- Traces tab: Calls with feedback
- Feedback display: reaction, note, and custom feedback
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
# 1. Feedback API - Add feedback to a traced call
# =============================================================================
print("\n" + "=" * 60)
print("1. Feedback API - Add feedback to a traced call")
print("=" * 60)


@weave.op()
def answer_question(question: str) -> str:
    """Run Q&A and add feedback to the returned call afterwards."""
    messages = [
        {"role": "system", "content": "Answer briefly and clearly."},
        {"role": "user", "content": question},
    ]
    return chat_completion(messages, max_tokens=120)


answer, call = answer_question.call("What is W&B Weave used for?")
print(f"Answer: {answer[:80]}...")

# Add reaction / note / arbitrary structured feedback from the SDK
reaction_id = call.feedback.add_reaction("👍")
note_id = call.feedback.add_note("Concise and easy to understand")
score_id = call.feedback.add("quality_score", {"value": 4})
print(f"Feedback IDs: reaction={reaction_id}, note={note_id}, score={score_id}")
print(f"Added feedback to call: {call.id}")


print("\n" + "=" * 60)
print("Online Feedback Demo Complete!")
print("=" * 60)
print("""
Summary:
- Add reactions with call.feedback.add_reaction()
- Add notes with call.feedback.add_note()
- Add arbitrary structured feedback with call.feedback.add()

Check in Weave UI:
- Use the Traces tab to inspect calls with feedback
- Use the Feedback display to inspect reactions, notes, and custom feedback
""")
