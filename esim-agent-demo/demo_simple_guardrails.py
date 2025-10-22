"""
Simple eSIM Agent Demo with Guardrails

Demonstrates using scorers as guardrails for RAG Agent responses.
This version uses direct scorer calls for simplicity and immediate feedback.
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

# Initialize scorers at module level for efficiency
faithfulness_guard = RAGFaithfulnessScorer()
relevancy_guard = RAGAnswerRelevancyScorer()
citation_monitor = RAGSourceCitationScorer()


@weave.op()
async def generate_rag_response(prompt: str) -> str:
    """
    Generate a response using the agent system.
    
    Args:
        prompt: User input
        
    Returns:
        Agent response
    """
    esim_agent = create_esim_agent()
    result = await Runner.run(esim_agent, prompt)
    return result.final_output


async def run_with_guardrails(prompt: str):
    """
    Run the agent with guardrail scoring.
    
    Args:
        prompt: User input
        
    Returns:
        Agent response with guardrail information
    """
    # Generate response (with Weave tracing)
    output, call = await generate_rag_response.call(prompt)
    output_str = str(output)
    
    print(f"\n{'='*80}")
    print("🛡️ Applying Guardrails...")
    print(f"{'='*80}\n")
    
    # Prepare model_output dict (scorers expect this format)
    model_output_dict = {"output": output_str}
    
    try:
        # Check faithfulness
        print("  Checking faithfulness (is response grounded in knowledge base)...")
        faithfulness_result = faithfulness_guard.score(
            model_output=model_output_dict,
            input=prompt
        )
        faithfulness_ok = faithfulness_result.get('faithfulness', False)
        print(f"  ✅ Faithfulness: {faithfulness_ok}")
        
        # Check answer relevancy
        print("  Checking relevancy (does it answer the question)...")
        relevancy_result = relevancy_guard.score(
            model_output=model_output_dict,
            input=prompt
        )
        relevancy_ok = relevancy_result.get('answer_relevancy', False)
        print(f"  ✅ Relevancy: {relevancy_ok}")
        
        # Check source citation (monitor only, not blocking)
        print("  Checking source citation (monitor only)...")
        citation_result = citation_monitor.score(
            model_output=model_output_dict
        )
        has_citation = citation_result.get('source_citation', False)
        print(f"  📚 Source Citation: {has_citation}")
        
        print(f"\n{'='*80}")
        
        # Guardrail logic: block if not faithful or not relevant
        if not faithfulness_ok:
            print(f"\n🚫 Response blocked: Not faithful to retrieved content")
            return "⚠️ I cannot provide a reliable answer. The information may not be accurate."
        
        if not relevancy_ok:
            print(f"\n🚫 Response blocked: Not relevant to your question")
            return "⚠️ I cannot provide a relevant answer. Please try rephrasing your question."
        
        print(f"\n✅ All guardrails passed! Response is safe to return.\n")
        
        # Provide feedback on citation
        if not has_citation:
            print(f"ℹ️  Note: Response does not include source citations (non-blocking).\n")
        
        return output_str
        
    except Exception as e:
        print(f"\n⚠️ Guardrail scoring failed: {e}")
        print("Proceeding with caution...\n")
        return output_str


async def demo():
    """
    Run a demo showing guardrails in action.
    """
    print("=" * 80)
    print("🛡️ eSIM Agent Demo - Simple Guardrails")
    print("=" * 80)
    print("\nThis demo shows how scorers can be used as guardrails to ensure")
    print("safe, accurate, and relevant responses from the RAG Agent.")
    print("\n" + "=" * 80 + "\n")
    
    # Test queries
    test_queries = [
        "How do I activate my eSIM?",
        "Is my iPhone 12 compatible with eSIM?",
        "What should I do if my eSIM isn't working?",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"📋 Query {i}/{len(test_queries)}: {query}")
        print(f"{'='*80}\n")
        
        try:
            response = await run_with_guardrails(query)
            print(f"\n📤 Final Response:\n{response}\n")
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
        
        # Small delay between queries
        if i < len(test_queries):
            await asyncio.sleep(2)
    
    print("=" * 80)
    print("✨ Demo completed!")
    print("=" * 80)


async def single_query(query: str):
    """
    Run a single query with guardrails.
    
    Args:
        query: User query to test
    """
    print(f"\n🧪 Testing query with guardrails: {query}\n")
    result = await run_with_guardrails(query)
    print(f"\n📤 Final Response:\n{result}\n")


if __name__ == "__main__":
    # Check if OPENAI_API_KEY is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable is not set.")
        print("Please set it in your .env file or environment.")
        exit(1)
    
    # Run guardrails demo
    asyncio.run(demo())
    
    # To run a single query, uncomment:
    # asyncio.run(single_query("How do I activate my eSIM?"))


# =============================================================================
# Guardrails Explanation
# =============================================================================
# 
# This demo implements guardrails using RAG scorers to ensure:
# 
# 1. Faithfulness (blocking): Response is grounded in retrieved content
# 2. Relevancy (blocking): Response actually answers the user's question
# 3. Source Citation (monitoring): Response includes proper citations
# 
# Guardrails vs Monitors:
# - Guardrails (blocking): Faithfulness, Relevancy
# - Monitors (non-blocking): Source Citation
# 
# The .call() method is used to get a Call object for Weave tracing.
# Scorers are called directly for simplicity and immediate feedback.
#

