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
from evaluation.scorers_rag import (
    RAGFaithfulnessScorer,
    RAGAnswerRelevancyScorer,
    RAGSourceCitationScorer,
)


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

# Initialize guardrail scorers at module level for efficiency
faithfulness_guard = RAGFaithfulnessScorer()
relevancy_guard = RAGAnswerRelevancyScorer()
citation_monitor = RAGSourceCitationScorer()


@weave.op()
async def _generate_agent_response(prompt: str) -> str:
    """
    Generate agent response (for Weave tracing and scorer application).
    
    Args:
        prompt: User input
        
    Returns:
        Agent response as string
    """
    esim_agent = create_esim_agent()
    response = await Runner.run(esim_agent, prompt)
    return str(response.final_output)


async def run_agent(prompt: str, apply_guardrails: bool = True, verbose: bool = False):
    """
    Run the agent with synchronous guardrail checking.
    
    If guardrails are enabled, checks:
    - Faithfulness: Response is grounded in knowledge base
    - Relevancy: Response answers the question
    - Source Citation: Response includes proper references (BLOCKING)
    
    Args:
        prompt: User input
        apply_guardrails: Whether to apply guardrail checks (default: True)
        verbose: Show guardrail checking progress (default: False)
        
    Returns:
        Agent response, or error message if guardrails fail
    """
    # Generate response and get Call object
    output, call = await _generate_agent_response.call(prompt)
    output_str = str(output)
    
    # If guardrails disabled, return immediately
    if not apply_guardrails:
        return output_str
    
    # Apply guardrails synchronously (blocking)
    if verbose:
        print(f"\n{'='*80}")
        print("🛡️ Applying Guardrails...")
        print(f"{'='*80}\n")
    
    try:
        model_output_dict = {"output": output_str}
        
        # Check faithfulness (is response grounded in knowledge base?)
        if verbose:
            print("  Checking faithfulness...")
        faithfulness_result = faithfulness_guard.score(
            model_output=model_output_dict,
            input=prompt
        )
        faithfulness_ok = faithfulness_result.get('faithfulness', False)
        if verbose:
            print(f"  ✅ Faithfulness: {faithfulness_ok}")
        
        # Check answer relevancy (does it answer the question?)
        if verbose:
            print("  Checking relevancy...")
        relevancy_result = relevancy_guard.score(
            model_output=model_output_dict,
            input=prompt
        )
        relevancy_ok = relevancy_result.get('answer_relevancy', False)
        if verbose:
            print(f"  ✅ Relevancy: {relevancy_ok}")
        
        # Check source citation (BLOCKING - critical for RAG)
        if verbose:
            print("  Checking source citation...")
        citation_result = citation_monitor.score(
            model_output=model_output_dict
        )
        has_citation = citation_result.get('source_citation', False)
        if verbose:
            print(f"  📚 Source Citation: {has_citation}")
            print(f"\n{'='*80}\n")
        
        # Apply guardrail logic (blocking)
        if not has_citation:
            if verbose:
                print("🚫 Response blocked: Missing source citations/references")
            return "⚠️ 申し訳ございません。適切な参照情報を含む回答を作成できませんでした。質問を言い換えてお試しください。"
        
        if not faithfulness_ok:
            if verbose:
                print("🚫 Response blocked: Not faithful to retrieved content")
            return "⚠️ 申し訳ございません。信頼できる回答を作成できませんでした。質問を言い換えてお試しください。"
        
        if not relevancy_ok:
            if verbose:
                print("🚫 Response blocked: Not relevant to your question")
            return "⚠️ 申し訳ございません。ご質問に関連する回答を作成できませんでした。質問を言い換えてお試しください。"
        
        # All guardrails passed
        if verbose:
            print("✅ All guardrails passed! Response is safe to return.\n")
        
        # Record scores to Weave asynchronously (non-blocking)
        asyncio.create_task(_record_scores_to_weave(call, output_str, prompt))
        
        return output_str
        
    except Exception as e:
        if verbose:
            print(f"⚠️ Guardrail error: {e}")
        # On error, return safe message
        return "⚠️ 申し訳ございません。回答の品質確認中にエラーが発生しました。もう一度お試しください。"


async def _record_scores_to_weave(call, output: str, prompt: str):
    """
    Record scorer results to Weave asynchronously (non-blocking).
    This runs in the background after the response is returned.
    """
    try:
        model_output_dict = {"output": output}
        
        # Record all scores to Weave in parallel
        await asyncio.gather(
            call.apply_scorer(
                faithfulness_guard,
                additional_scorer_kwargs={
                    "model_output": model_output_dict,
                    "input": prompt
                }
            ),
            call.apply_scorer(
                relevancy_guard,
                additional_scorer_kwargs={
                    "model_output": model_output_dict,
                    "input": prompt
                }
            ),
            call.apply_scorer(
                citation_monitor,
                additional_scorer_kwargs={"model_output": model_output_dict}
            ),
            return_exceptions=True
        )
    except Exception:
        pass  # Silent failure for background recording


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


async def single_query_demo(query: str, verbose: bool = True):
    """
    Run a single query demo (useful for testing).
    
    Args:
        query: User query to test
        verbose: Show guardrail checking progress (default: True)
    """
    print(f"\n🧪 Testing query: {query}\n")
    result = await run_agent(query, verbose=verbose)
    print(f"\n📤 Response:\n{result}\n")


async def run_sample_queries(verbose: bool = False):
    """
    Run 10 sample queries to demonstrate the eSIM agent system.
    
    Args:
        verbose: Show guardrail checking progress for each query (default: False)
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
    print("🧪 Running 10 Sample Queries with Guardrails")
    print("=" * 80)
    print(f"Verbose mode: {'ON' if verbose else 'OFF'}")
    print("=" * 80)
    
    for i, query in enumerate(sample_queries, 1):
        print(f"\n{'='*80}")
        print(f"📋 Query {i}/10: {query}")
        print(f"{'='*80}")
        
        try:
            result = await run_agent(query, verbose=verbose)
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

