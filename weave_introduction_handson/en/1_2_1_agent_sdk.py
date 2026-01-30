"""
1_2_1: Agent SDK - Building Agents

What you'll learn in this script:
================================
1. Tool Calling Tracing
2. Conversation Session Management with Threads
3. Agent Loop Visualization
"""

import os
import json
from dotenv import load_dotenv
import weave

from config_loader import chat_completion, get_model_name, load_config

# Load environment variables
load_dotenv()

# Initialize Weave
# Initialize with weave.init("entity/project")
weave.init(f"{os.getenv('WANDB_ENTITY')}/{os.getenv('WANDB_PROJECT', 'weave-handson')}")


# =============================================================================
# 1. Simple Tool Calling Agent
# =============================================================================
print("\n" + "=" * 60)
print("1. Simple Tool Calling Agent")
print("=" * 60)


@weave.op()
def get_weather(location: str, unit: str = "celsius") -> dict:
    """Mock weather API."""
    return {"location": location, "temperature": 22, "unit": unit, "condition": "Sunny"}


@weave.op()
def search_restaurants(location: str, cuisine: str = None) -> list:
    """Mock restaurant search."""
    return [
        {"name": f"Best {cuisine or 'Local'} Restaurant", "rating": 4.5},
        {"name": f"Popular {cuisine or 'Local'} Spot", "rating": 4.2},
    ]


@weave.op()
def run_agent(user_message: str) -> str:
    """Run a simple agent that uses tools.
    
    The agent's tool calling process is traced.
    """
    # Analyze user intent
    messages = [
        {"role": "system", "content": "Analyze the user's request and determine what information they need. Respond with JSON: {\"needs_weather\": bool, \"needs_restaurants\": bool, \"location\": str, \"cuisine\": str or null}"},
        {"role": "user", "content": user_message},
    ]
    
    try:
        intent = json.loads(chat_completion(messages, temperature=0))
    except:
        intent = {"needs_weather": False, "needs_restaurants": False}
    
    # Execute tools based on intent
    context = []
    location = intent.get("location", "Tokyo")
    
    if intent.get("needs_weather"):
        weather = get_weather(location)
        context.append(f"Weather in {location}: {weather['temperature']}°C, {weather['condition']}")
    
    if intent.get("needs_restaurants"):
        cuisine = intent.get("cuisine")
        restaurants = search_restaurants(location, cuisine)
        context.append(f"Restaurants: {restaurants}")
    
    # Generate final response
    final_messages = [
        {"role": "system", "content": "You are a helpful travel assistant. Use the provided context to answer."},
        {"role": "user", "content": f"Context: {context}\n\nUser question: {user_message}"},
    ]
    
    return chat_completion(final_messages)


result = run_agent("What's the weather like in Tokyo and recommend some sushi restaurants?")
print(f"Agent response:\n{result}")
print("\nCheck agent tool calls in Weave UI")


# =============================================================================
# 2. Multi-turn Conversation with Threads
# =============================================================================
print("\n" + "=" * 60)
print("2. Multi-turn Conversation with Threads")
print("=" * 60)


class ChatSession:
    """A chat session using threads for grouping."""
    
    def __init__(self):
        self.messages = []
    
    @weave.op()
    def send_message(self, user_message: str) -> str:
        """Send a message in this session."""
        self.messages.append({"role": "user", "content": user_message})
        
        all_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            *self.messages,
        ]
        
        response = chat_completion(all_messages)
        self.messages.append({"role": "assistant", "content": response})
        return response


session = ChatSession()

# All messages in this thread will be grouped together
with weave.thread() as thread_ctx:
    print(f"Thread ID: {thread_ctx.thread_id}")
    
    r1 = session.send_message("What is machine learning?")
    print(f"Turn 1: {r1[:80]}...")
    
    r2 = session.send_message("Give me a simple example.")
    print(f"Turn 2: {r2[:80]}...")

print("\nCheck sessions in the Threads tab in Weave UI")


print("\n" + "=" * 60)
print("Agent SDK Demo Complete!")
print("=" * 60)
