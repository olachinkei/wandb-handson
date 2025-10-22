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
from evaluation.scorers_rag import RAGSourceCitationScorer
from evaluation.scorers import QueryCategorizationScorer


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

# Initialize scorers at module level
citation_scorer = RAGSourceCitationScorer()
query_categorization_scorer = QueryCategorizationScorer()


@weave.op()
async def run_agent(prompt: str):
    """
    Core agent execution function (Weave-tracked).
    
    This function simply runs the agent and returns the response.
    Use run_agent_with_guardrails() to apply citation checking.
    
    Args:
        prompt: User input
        
    Returns:
        Agent response as string
    """
    esim_agent = create_esim_agent()
    response = await Runner.run(esim_agent, prompt)
    return str(response.final_output)


async def run_agent_with_guardrails(prompt: str, verbose: bool = False):
    """
    Run the agent with intelligent guardrails.
    
    This function:
    1. Runs the agent to get the Call object
    2. Applies query categorization scorer to the Call
    3. For RAG queries: Applies citation scorer to the Call
    4. All scores are associated with the run_agent Call in Weave UI
    
    Args:
        prompt: User input
        verbose: Show guardrail checking progress (default: False)
        
    Returns:
        Agent response, or error message if citation check fails (RAG queries only)
    """
    # Step 1: Run agent and get Call object
    if verbose:
        print(f"\n{'='*80}")
        print("🤖 Step 1: Running Agent...")
        print(f"{'='*80}\n")
    
    output, call = await run_agent.call(prompt)
    output_str = str(output)
    
    # Step 2: Apply categorization scorer to the run_agent Call
    if verbose:
        print(f"{'='*80}")
        print("🔍 Step 2: Categorizing Query (LLM-as-a-Judge)...")
        print(f"{'='*80}\n")
    
    try:
        categorization_result = await call.apply_scorer(
            query_categorization_scorer,
            additional_scorer_kwargs={
                "output": output_str,
                "input": prompt
            }
        )
        
        # Extract categorization from the scorer result (handle different return types)
        result_data = categorization_result.result
        if isinstance(result_data, dict):
            category = result_data.get("category", "UNKNOWN")
            sub_category = result_data.get("sub_category", "unknown")
            reasoning = result_data.get("reasoning", "")
        elif hasattr(result_data, 'category'):
            category = getattr(result_data, 'category', 'UNKNOWN')
            sub_category = getattr(result_data, 'sub_category', 'unknown')
            reasoning = getattr(result_data, 'reasoning', '')
        else:
            category = "UNKNOWN"
            sub_category = "unknown"
            reasoning = ""
        
        if verbose:
            print(f"  📂 Category: {category}")
            print(f"  📁 Sub-category: {sub_category}")
            print(f"  💭 Reasoning: {reasoning}")
            print(f"\n{'='*80}\n")
    except Exception as e:
        if verbose:
            print(f"  ⚠️ Categorization failed: {e}\n")
        category = "UNKNOWN"
        sub_category = "unknown"
    
    # Step 3: Apply citation guardrail ONLY for RAG_QUESTION and MIXED queries
    is_rag_query = category in ["RAG_QUESTION", "MIXED"]
    
    if is_rag_query:
        if verbose:
            print(f"{'='*80}")
            print("🛡️ Step 3: Applying Citation Guardrail (RAG Query Detected)...")
            print(f"{'='*80}\n")
        
        try:
            # Apply citation scorer to the run_agent Call object
            # This associates the score with the run_agent Call in Weave UI
            model_output_dict = {"output": output_str}
            citation_result = await call.apply_scorer(
                citation_scorer,
                additional_scorer_kwargs={"model_output": model_output_dict}
            )
            
            # Extract score result
            result_data = citation_result.result
            if isinstance(result_data, dict):
                has_citation = result_data.get('source_citation', False)
            elif hasattr(result_data, 'source_citation'):
                has_citation = getattr(result_data, 'source_citation', False)
            else:
                has_citation = False
            
            if verbose:
                print(f"  📚 Source Citation: {has_citation}")
                print(f"\n{'='*80}\n")
            
            # Block response if no citations
            if not has_citation:
                if verbose:
                    print("🚫 Response blocked: Missing source citations/references\n")
                return "⚠️ 申し訳ございません。適切な参照情報を含む回答を作成できませんでした。質問を言い換えてお試しください。"
            
            # Citation check passed
            if verbose:
                print("✅ Citation check passed! Response includes proper references.\n")
            
        except Exception as e:
            if verbose:
                print(f"⚠️ Citation scorer error: {e}\n")
            # On error, still return the response (fail-open)
            pass
    else:
        if verbose:
            print(f"{'='*80}")
            print(f"ℹ️  Step 3: Skipping Citation Check (Category: {category})")
            print(f"{'='*80}\n")
            print(f"  Citation guardrail only applies to RAG_QUESTION and MIXED queries.\n")
    
    return output_str


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
    Run a single query demo with citation guardrails (useful for testing).
    
    Args:
        query: User query to test
        verbose: Show guardrail checking progress (default: True)
    """
    print(f"\n🧪 Testing query: {query}\n")
    result = await run_agent_with_guardrails(query, verbose=verbose)
    print(f"\n📤 Response:\n{result}\n")


async def run_comprehensive_scenarios(verbose: bool = False):
    """
    Run comprehensive test scenarios covering all agent capabilities.
    
    Scenarios covered:
    - Plan Search (basic, regional, global, unavailable countries)
    - RAG Questions (device compatibility, activation, troubleshooting, security)
    - Booking (direct purchase, flow with authentication)
    - Mixed (plan search + how-to questions)
    - Out of Scope (completely unrelated questions)
    - Ambiguous (unclear user intent)
    
    Args:
        verbose: Show guardrail checking progress for each query (default: False)
    """
    scenarios = [
        # ============================================================
        # 📋 PLAN SEARCH SCENARIOS (8 scenarios)
        # ============================================================
        ("Plan Search: Basic - Japan", 
         "I need an eSIM plan for Japan, 7 days"),
        
        ("Plan Search: Basic with dates - USA",
         "I'm visiting the USA from Nov 15 to Nov 25"),
        
        ("Plan Search: Regional - Europe",
         "Find me a plan for France and Italy, 14 days total"),
        
        ("Plan Search: Regional - Asia",
         "I'm traveling to Thailand, Vietnam, and Singapore for 3 weeks"),
        
        ("Plan Search: Global",
         "I need a global eSIM plan for my around-the-world trip, 30 days"),
        
        ("Plan Search: Short duration",
         "Quick 3-day trip to South Korea"),
        
        ("Plan Search: Unsupported country",
         "Do you have plans for North Korea?"),
        
        ("Plan Search: Ambiguous",
         "I need a plan for Asia"),
        
        # ============================================================
        # 📚 RAG QUESTION SCENARIOS (8 scenarios)
        # ============================================================
        ("RAG: Device compatibility - iPhone",
         "Is my iPhone 12 compatible with eSIM?"),
        
        ("RAG: Device compatibility - Android",
         "Can I use eSIM on my Samsung Galaxy S21?"),
        
        ("RAG: Activation",
         "How do I activate my eSIM after purchasing?"),
        
        ("RAG: Setup process",
         "What's the step-by-step process to set up an eSIM?"),
        
        ("RAG: Troubleshooting - connectivity",
         "My eSIM isn't connecting to the network, what should I do?"),
        
        ("RAG: Troubleshooting - installation",
         "I can't install my eSIM, help!"),
        
        ("RAG: Security",
         "Is eSIM secure? Can someone steal my eSIM data?"),
        
        ("RAG: General info",
         "What are the advantages of eSIM over physical SIM?"),
        
        # ============================================================
        # 🛒 BOOKING SCENARIOS (4 scenarios)
        # ============================================================
        ("Booking: Direct purchase",
         "I want to buy the 7-day Japan plan for $6.50"),
        
        ("Booking: With quantity",
         "I'd like to purchase 2 units of the Europe regional plan"),
        
        ("Booking: After plan search",
         "I'll take the 14-day France plan"),
        
        ("Booking: Ambiguous",
         "I want to buy a plan"),
        
        # ============================================================
        # 🔀 MIXED SCENARIOS (5 scenarios)
        # ============================================================
        ("Mixed: Plan search + how-to",
         "I need a plan for Spain and want to know how to activate it"),
        
        ("Mixed: Plan search + device check",
         "Do you have plans for Australia? Also, will it work on my iPhone 14?"),
        
        ("Mixed: Plan search + troubleshooting",
         "I need a plan for Germany, but last time I had connection issues"),
        
        ("Mixed: Full journey",
         "I'm going to Italy for 10 days, need a plan, how do I set it up, and how do I buy it?"),
        
        ("Mixed: Device check + plan + booking",
         "Does my Samsung support eSIM? If yes, I need a 7-day plan for Japan and want to buy it"),
        
        # ============================================================
        # ❌ OUT OF SCOPE SCENARIOS (3 scenarios)
        # ============================================================
        ("Out of Scope: Weather",
         "What's the weather like in Tokyo?"),
        
        ("Out of Scope: Restaurant",
         "Can you recommend a good Italian restaurant in Paris?"),
        
        ("Out of Scope: Stock market",
         "What's the stock price of telecommunication companies?"),
        
        # ============================================================
        # 🤔 AMBIGUOUS / EDGE CASE SCENARIOS (2 scenarios)
        # ============================================================
        ("Ambiguous: No destination",
         "I need a plan"),
        
        ("Ambiguous: No duration",
         "How much for Japan?"),
    ]
    
    print("=" * 80)
    print("🧪 COMPREHENSIVE SCENARIO TESTING")
    print("=" * 80)
    print(f"Total scenarios: {len(scenarios)}")
    print(f"Verbose mode: {'ON' if verbose else 'OFF'}")
    print("=" * 80)
    
    results = {
        "success": 0,
        "blocked": 0,
        "error": 0
    }
    
    for i, (scenario_name, query) in enumerate(scenarios, 1):
        print(f"\n{'='*80}")
        print(f"📋 Scenario {i}/{len(scenarios)}: {scenario_name}")
        print(f"{'='*80}")
        print(f"💬 Query: {query}")
        print("-" * 80)
        
        try:
            result = await run_agent_with_guardrails(query, verbose=verbose)
            
            # Detect response type
            is_blocked = "申し訳ございません" in result and "参照情報" in result
            
            # Check if providing substantial information
            info_indicators = ["according to", "our knowledge", "here are", "i found", 
                             "available", "option", "countries covered", "duration:", "data:"]
            has_substantial_info = any(indicator in result.lower() for indicator in info_indicators)
            
            # Check if asking for clarification
            question_markers = ["which", "what", "how many", "please tell", "please give",
                              "could you", "would you", "can you tell", "are you looking"]
            has_question_markers = any(marker in result.lower() for marker in question_markers)
            
            # Short response with question markers = asking clarification
            is_short_question = len(result) < 300 and has_question_markers
            
            # Determine if asking question (not providing substantial info OR is a short question)
            is_asking_question = (has_question_markers and not has_substantial_info) or is_short_question
            
            if is_blocked:
                print(f"\n🚫 BLOCKED (Citation failure)")
                results["blocked"] += 1
            elif is_asking_question:
                print(f"\n🤔 ASKING CLARIFICATION (Agent needs more info)")
                results["success"] += 1
            else:
                print(f"\n✅ SUCCESS (Complete answer provided)")
                results["success"] += 1
            
            # Print full response (not truncated) for better visibility
            print(f"\n📤 Agent Response:")
            print(f"{'-'*80}")
            if len(result) > 300:
                # Show first 300 chars if too long
                print(f"{result[:300]}...")
                print(f"\n... (truncated, {len(result)} chars total)")
            else:
                print(result)
            print(f"{'-'*80}")
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            results["error"] += 1
        
        # Small delay between queries
        await asyncio.sleep(1.5)
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 SCENARIO TEST SUMMARY")
    print("=" * 80)
    print(f"Total scenarios: {len(scenarios)}")
    print(f"✅ Success: {results['success']} ({results['success']/len(scenarios)*100:.1f}%)")
    print(f"🚫 Blocked: {results['blocked']} ({results['blocked']/len(scenarios)*100:.1f}%)")
    print(f"❌ Error: {results['error']} ({results['error']/len(scenarios)*100:.1f}%)")
    print("=" * 80)
    print(f"✨ Check Weave UI: https://wandb.ai/agent-lab/esim-agent/weave")
    print("=" * 80)


async def run_sample_queries(verbose: bool = False):
    """
    Run 10 quick sample queries with citation guardrails.
    
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
    print("🧪 Running 10 Sample Queries with Citation Guardrails")
    print("=" * 80)
    print(f"Verbose mode: {'ON' if verbose else 'OFF'}")
    print("=" * 80)
    
    for i, query in enumerate(sample_queries, 1):
        print(f"\n{'='*80}")
        print(f"📋 Query {i}/10: {query}")
        print(f"{'='*80}")
        
        try:
            result = await run_agent_with_guardrails(query, verbose=verbose)
            print(f"\n✅ Response:\n{result}\n")
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
        
        # Small delay between queries
        await asyncio.sleep(1)
    
    print("=" * 80)
    print("✨ Sample queries completed!")
    print("=" * 80)


if __name__ == "__main__":
    import sys
    
    # Check if OPENAI_API_KEY is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable is not set.")
        print("Please set it in your .env file or environment.")
        exit(1)
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        verbose = "--verbose" in sys.argv or "-v" in sys.argv
        
        if mode == "comprehensive":
            print("\n🚀 Running comprehensive scenario tests (30 scenarios)...\n")
            asyncio.run(run_comprehensive_scenarios(verbose=verbose))
        elif mode == "sample":
            print("\n🚀 Running quick sample queries (10 queries)...\n")
            asyncio.run(run_sample_queries(verbose=verbose))
        elif mode == "interactive":
            print("\n🚀 Starting interactive demo...\n")
            asyncio.run(interactive_demo())
        elif mode == "help" or mode == "-h" or mode == "--help":
            print("""
eSIM Agent Demo - Usage
=======================

Run modes:
  comprehensive    Run 30 comprehensive scenarios covering all capabilities
  sample           Run 10 quick sample queries (default)
  interactive      Start interactive chat mode
  
Options:
  --verbose, -v    Show detailed guardrail checking progress

Examples:
  python demo.py comprehensive          # Run all 30 scenarios
  python demo.py comprehensive -v       # Run all scenarios with verbose output
  python demo.py sample                 # Run 10 quick samples
  python demo.py interactive            # Interactive chat mode

Scenario Categories (comprehensive mode):
  📋 Plan Search (8): Basic, regional, global, unsupported countries
  📚 RAG Questions (8): Device compatibility, activation, troubleshooting
  🛒 Booking (4): Direct purchase, with quantity, after search
  🔀 Mixed (5): Combined plan search + RAG + booking
  ❌ Out of Scope (3): Unrelated questions
  🤔 Ambiguous (2): Unclear user intent
  
  Total: 30 scenarios

For more information, see README.md
""")
            exit(0)
        else:
            print(f"❌ Unknown mode: {mode}")
            print("Run 'python demo.py help' for usage information")
            exit(1)
    else:
        # Default: run comprehensive scenarios
        print("\n🚀 Running comprehensive scenario tests (30 scenarios)...")
        print("   Tip: Use 'python demo.py help' to see all options\n")
        asyncio.run(run_comprehensive_scenarios(verbose=False))


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

