"""
eSIM Agent Demo

Interactive demo for the eSIM multi-agent system.
"""

import asyncio
import os
from dotenv import load_dotenv

import weave
from agents import Runner, set_trace_processors
from weave.integrations.openai_agents.openai_agents import WeaveTracingProcessor

from src.utils import load_config
from src.agents import create_esim_agent


# Load environment variables
load_dotenv()

# Load configuration
config = load_config()

# Initialize Weave tracing
weave_config = config["weave"]
project_name = f"{weave_config['entity']}/{weave_config['project']}"
weave.init(project_name=project_name)

# Set up OpenAI Agents tracing processor
set_trace_processors([WeaveTracingProcessor()])


@weave.op()
async def run_agent(prompt: str):
    """
    Run the agent with a single prompt.
    
    Args:
        prompt: User input
        
    Returns:
        Agent response
    """
    esim_agent = create_esim_agent()
    response = await Runner.run(esim_agent, prompt)
    return response.final_output


@weave.op()
async def interactive_demo():
    """
    Run an interactive demo session with the eSIM agent system.
    """
    print("=" * 80)
    print("🌍 eSIM Agent Demo - Multi-Agent System")
    print("=" * 80)
    print("\nWelcome! I'm here to help you with all your eSIM needs.")
    print("\nYou can ask me about:")
    print("  • Finding eSIM plans for your travels")
    print("  • General eSIM questions (setup, compatibility, etc.)")
    print("  • Booking and purchasing eSIM plans")
    print("\nType 'quit' or 'exit' to end the session.\n")
    print("=" * 80)
    
    # Create main agent
    esim_agent = create_esim_agent()
    
    previous_response_id = None
    current_agent = esim_agent
    
    while True:
        try:
            # Get user input
            user_input = input("\n👤 You: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
                print("\n🤖 Agent: Thank you for using eSIM Agent Demo. Have a great day! 👋\n")
                break
            
            # Run agent
            print("\n🤖 Agent: ", end="", flush=True)
            response = await Runner.run(
                current_agent,
                user_input,
                previous_response_id=previous_response_id
            )
            
            # Update state
            previous_response_id = response.last_response_id
            current_agent = response.last_agent
            
            # Print response
            agent_name = current_agent.name
            if agent_name != "eSIM Agent":
                print(f"[{agent_name}]", end=" ")
            print(response.final_output)
            
        except KeyboardInterrupt:
            print("\n\n🤖 Agent: Session interrupted. Goodbye! 👋\n")
            break
        except Exception as e:
            print(f"\n\n❌ Error: {e}")
            print("Please try again or type 'quit' to exit.\n")


async def single_query_demo(query: str):
    """
    Run a single query demo (useful for testing).
    
    Args:
        query: User query to test
    """
    print(f"\n🧪 Testing query: {query}\n")
    result = await run_agent(query)
    print(f"\n📤 Response:\n{result}\n")


async def run_sample_queries():
    """
    Run 10 sample queries to demonstrate the eSIM agent system.
    """
    sample_queries = [
        # Plan Search queries (3)
        "I'm traveling to Japan for 7 days",
        "Find me an eSIM plan for France and Italy, 14 days total",
        "What plans do you have for Thailand?",
        
        # RAG queries (3)
        "How do I activate my eSIM?",
        "Is my iPhone 12 compatible with eSIM?",
        "What should I do if my eSIM isn't working?",
        
        # Booking flow queries (2)
        "I want to buy the 7-day Japan plan",
        "Can I purchase the Europe regional plan now?",
        
        # Mixed/Complex queries (2)
        "I need an eSIM for Spain, how does it work and can I buy it?",
        "What's the best plan for a 10-day trip to Australia and how do I set it up?"
    ]
    
    print("=" * 80)
    print("🧪 Running 10 Sample Queries")
    print("=" * 80)
    
    for i, query in enumerate(sample_queries, 1):
        print(f"\n{'='*80}")
        print(f"📋 Query {i}/10: {query}")
        print(f"{'='*80}")
        
        try:
            result = await run_agent(query)
            print(f"\n✅ Response:\n{result}\n")
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
        
        # Small delay between queries
        await asyncio.sleep(1)
    
    print("=" * 80)
    print("✨ Sample queries completed!")
    print("=" * 80)


if __name__ == "__main__":
    # Check if OPENAI_API_KEY is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable is not set.")
        print("Please set it in your .env file or environment.")
        exit(1)
    
    # Run sample queries demo
    asyncio.run(run_sample_queries())
    
    # To run interactive demo instead, uncomment:
    # asyncio.run(interactive_demo())
    
    # To run a single query, uncomment:
    # asyncio.run(single_query_demo("I'm traveling to Japan for 7 days"))


# =============================================================================
# Sample Queries for Testing
# =============================================================================
# 
# Plan Search Queries:
# 1. "I'm traveling to Japan for 7 days"
# 2. "Find me an eSIM plan for France and Italy, 14 days total"
# 3. "What plans do you have for Thailand?"
# 
# RAG Queries:
# 4. "How do I activate my eSIM?"
# 5. "Is my iPhone 12 compatible with eSIM?"
# 6. "What should I do if my eSIM isn't working?"
# 
# Booking Flow Queries:
# 7. "I want to buy the 7-day Japan plan"
# 8. "Can I purchase the Europe regional plan now?"
# 
# Mixed/Complex Queries:
# 9. "I need an eSIM for Spain, how does it work and can I buy it?"
# 10. "What's the best plan for a 10-day trip to Australia and how do I set it up?"
#

