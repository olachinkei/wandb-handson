"""
eSIM Agent Evaluation Runner

Runs Weave evaluations for all agent types with comprehensive scoring.
"""

import asyncio
import json
from pathlib import Path
from typing import Any, Optional, Dict, List
from dotenv import load_dotenv

import weave
from agents import Agent, Runner, set_trace_processors
from pydantic import Field
from weave.integrations.openai_agents.openai_agents import WeaveTracingProcessor

from src.utils import load_config, get_project_root
from src.agents import (
    create_esim_agent,
    create_plan_search_agent,
    create_booking_agent,
    create_rag_agent,
)
from evaluation.scorers_plan_search import PLAN_SEARCH_SCORERS
from evaluation.scorers_rag import RAG_SCORERS
from evaluation.scorers_booking import BOOKING_SCORERS
from evaluation.scorers_end_to_end import END_TO_END_SCORERS

# Load environment
load_dotenv()

# Set up Weave tracing
set_trace_processors([WeaveTracingProcessor()])

# Load configuration
config = load_config()
weave_config = config["weave"]
project_name = f"{weave_config['entity']}/{weave_config['project']}"

# Initialize Weave
weave.init(project_name=project_name)


# =============================================================================
# Agent Model Wrapper
# =============================================================================

class AgentModel(weave.Model):
    """
    Wrapper for agents to work with Weave evaluations.
    """
    name: Optional[str] = None
    agent: Any = Field(default=None)
    
    def __init__(self, agent: Agent, name: str = None):
        super().__init__()
        self.agent = agent
        self.name = name if name else agent.name
    
    @weave.op()
    async def predict(self, input: str, **kwargs) -> dict:
        """
        Run the agent and return structured output.
        
        Args:
            input: User input/query
            **kwargs: Additional context (e.g., user_id, plan_price)
            
        Returns:
            Dictionary with agent output and metadata
        """
        result = await Runner.run(self.agent, input)
        
        # Extract tool calls, agent sequence, and step count from new_items
        tool_calls = []
        agent_sequence = []
        current_agent = None
        step_count = 0
        
        for item in result.new_items:
            # Count all significant items as steps
            if hasattr(item, "type"):
                step_count += 1
                
                # Track tool calls
                if item.type == "tool_call_item":
                    if hasattr(item, "raw_item"):
                        # Remove '_impl' suffix if present for consistency with expected names
                        tool_name = item.raw_item.name
                        if tool_name.endswith("_impl"):
                            tool_name = tool_name[:-5]  # Remove last 5 characters ('_impl')
                        tool_calls.append(tool_name)
                
                # Track agent sequence from any item that has agent info
                if hasattr(item, "agent") and item.agent:
                    agent_name = item.agent.name if hasattr(item.agent, "name") else str(item.agent)
                    # Add to sequence if it's a new agent
                    if agent_name != current_agent:
                        if agent_name not in agent_sequence:
                            agent_sequence.append(agent_name)
                        current_agent = agent_name
        
        # Ensure the last agent is in the sequence
        if result.last_agent and result.last_agent.name not in agent_sequence:
            agent_sequence.append(result.last_agent.name)
        
        return {
            "output": result.final_output,
            "final_output": result.final_output,  # For compatibility
            "tool_calls": tool_calls,
            "agent_sequence": agent_sequence,
            "step_count": step_count,
            "last_agent": result.last_agent.name,
            "new_items": result.new_items,
            "has_error": False,  # Can be enhanced to detect errors
        }


# =============================================================================
# Dataset Loading
# =============================================================================

def load_scenarios(scenario_file: str) -> List[dict]:
    """
    Load evaluation scenarios from JSON file.
    
    Args:
        scenario_file: Path to scenario JSON file
        
    Returns:
        List of scenario dictionaries
    """
    project_root = get_project_root()
    scenario_path = project_root / "evaluation" / "scenarios" / scenario_file
    
    with open(scenario_path, 'r') as f:
        scenarios = json.load(f)
    
    return scenarios


def prepare_plan_search_dataset() -> List[dict]:
    """Prepare Plan Search evaluation dataset."""
    scenarios = load_scenarios("plan_search_scenarios.json")
    
    dataset = []
    for scenario in scenarios:
        dataset.append({
            "input": scenario["input"],
            "expected_tool_calls": scenario["expected_tool_calls"],
            "expected_countries": scenario["expected_countries"],
            "expected_days": scenario["expected_days"],
            "expected_plan_type": scenario.get("expected_plan_type"),
            "expected_plan_price": scenario.get("expected_plan_price"),
            "expected_booking_prompt": scenario["expected_booking_prompt"],
            "expected_service_available": scenario["expected_service_available"],
            "is_ambiguous": scenario.get("is_ambiguous", False),
            "id": scenario["id"],
        })
    
    return dataset


def prepare_rag_dataset() -> List[dict]:
    """Prepare RAG evaluation dataset."""
    scenarios = load_scenarios("rag_scenarios.json")
    
    dataset = []
    for scenario in scenarios:
        dataset.append({
            "input": scenario["input"],
            "expected_tool_calls": scenario.get("expected_tool_calls", []),
            "expected_topics": scenario.get("expected_topics", []),
            "expected_out_of_scope": scenario.get("expected_out_of_scope", False),
            "expected_redirect": scenario.get("expected_redirect"),
            "expected_answer_relevance": scenario.get("expected_answer_relevance"),
            "is_ambiguous": scenario.get("is_ambiguous", False),
            "id": scenario["id"],
        })
    
    return dataset


def prepare_booking_dataset() -> List[dict]:
    """Prepare Booking evaluation dataset."""
    scenarios = load_scenarios("booking_scenarios.json")
    
    dataset = []
    for scenario in scenarios:
        dataset.append({
            "input": scenario["input"],
            "user_id": scenario.get("user_id", "user_001"),
            "plan_price": scenario.get("plan_price", 0.0),
            "quantity": scenario.get("quantity", 1),
            "expected_tool_calls": scenario["expected_tool_calls"],
            "expected_ready_to_book": scenario.get("expected_ready_to_book", False),
            "expected_prompt_login": scenario.get("expected_prompt_login", False),
            "expected_prompt_payment": scenario.get("expected_prompt_payment", False),
            "expected_total": scenario.get("expected_total"),
            "is_ambiguous": scenario.get("is_ambiguous", False),
            "id": scenario["id"],
        })
    
    return dataset


def prepare_end_to_end_dataset() -> List[dict]:
    """Prepare End-to-End evaluation dataset."""
    scenarios = load_scenarios("end_to_end_scenarios.json")
    
    dataset = []
    for scenario in scenarios:
        dataset.append({
            "input": scenario["input"],
            "user_id": scenario.get("user_id", "user_001"),
            "expected_agent_sequence": scenario.get("expected_agent_sequence", []),
            "expected_tools": scenario.get("expected_tools", []),
            "intermediate_checks": scenario.get("intermediate_checks", {}),
            "final_checks": scenario.get("final_checks", {}),
            "expected_final_output_description": scenario.get("expected_final_output_description", ""),
            "expected_step_range": scenario.get("expected_step_range", [1, 50]),
            "expected_success": scenario.get("expected_success", True),
            "is_ambiguous": scenario.get("is_ambiguous", False),
            "id": scenario["id"],
        })
    
    return dataset


# =============================================================================
# Evaluation Functions
# =============================================================================

async def evaluate_plan_search_agent():
    """Evaluate Plan Search Agent."""
    print("\n" + "="*70)
    print("🔍 Evaluating Plan Search Agent")
    print("="*70)
    
    # Create agent and model
    agent = create_plan_search_agent()
    model = AgentModel(agent, name="Plan_Search_Agent")
    
    # Prepare dataset
    dataset = prepare_plan_search_dataset()
    print(f"📊 Dataset: {len(dataset)} scenarios")
    
    # Create evaluation
    evaluation = weave.Evaluation(
        name="plan_search_evaluation",
        dataset=dataset,
        scorers=PLAN_SEARCH_SCORERS,
    )
    
    # Run evaluation
    print("🚀 Running evaluation...")
    results = await evaluation.evaluate(
        model,
        __weave={"display_name": "Plan Search Agent Evaluation"}
    )
    
    # Print summary
    print("\n📈 Results Summary:")
    for metric, scores in results.items():
        if isinstance(scores, dict) and "mean" in scores:
            print(f"  {metric}: {scores['mean']:.2%}")
    
    return results


async def evaluate_rag_agent():
    """Evaluate RAG Agent."""
    print("\n" + "="*70)
    print("📚 Evaluating RAG Agent")
    print("="*70)
    
    # Create agent and model
    agent = create_rag_agent()
    model = AgentModel(agent, name="RAG_Agent")
    
    # Prepare dataset
    dataset = prepare_rag_dataset()
    print(f"📊 Dataset: {len(dataset)} scenarios")
    
    # Create evaluation
    evaluation = weave.Evaluation(
        name="rag_evaluation",
        dataset=dataset,
        scorers=RAG_SCORERS,
    )
    
    # Run evaluation
    print("🚀 Running evaluation...")
    results = await evaluation.evaluate(
        model,
        __weave={"display_name": "RAG Agent Evaluation"}
    )
    
    # Print summary
    print("\n📈 Results Summary:")
    for metric, scores in results.items():
        if isinstance(scores, dict) and "mean" in scores:
            print(f"  {metric}: {scores['mean']:.2%}")
    
    return results


async def evaluate_booking_agent():
    """Evaluate Booking Agent."""
    print("\n" + "="*70)
    print("💳 Evaluating Booking Agent")
    print("="*70)
    
    # Create agent and model
    agent = create_booking_agent()
    model = AgentModel(agent, name="Booking_Agent")
    
    # Prepare dataset
    dataset = prepare_booking_dataset()
    print(f"📊 Dataset: {len(dataset)} scenarios")
    
    # Create evaluation
    evaluation = weave.Evaluation(
        name="booking_evaluation",
        dataset=dataset,
        scorers=BOOKING_SCORERS,
    )
    
    # Run evaluation
    print("🚀 Running evaluation...")
    results = await evaluation.evaluate(
        model,
        __weave={"display_name": "Booking Agent Evaluation"}
    )
    
    # Print summary
    print("\n📈 Results Summary:")
    for metric, scores in results.items():
        if isinstance(scores, dict) and "mean" in scores:
            print(f"  {metric}: {scores['mean']:.2%}")
    
    return results


async def evaluate_end_to_end_system():
    """Evaluate End-to-End System (complete workflow across multiple agents)."""
    print("\n" + "="*70)
    print("🔗 Evaluating End-to-End System")
    print("="*70)
    
    # Create main eSIM agent (orchestrator)
    agent = create_esim_agent()
    model = AgentModel(agent, name="eSIM_Agent_System")
    
    # Prepare dataset
    dataset = prepare_end_to_end_dataset()
    print(f"📊 Dataset: {len(dataset)} scenarios")
    
    # Create evaluation
    evaluation = weave.Evaluation(
        name="end_to_end_evaluation",
        dataset=dataset,
        scorers=END_TO_END_SCORERS,
    )
    
    # Run evaluation
    print("🚀 Running evaluation...")
    results = await evaluation.evaluate(
        model,
        __weave={"display_name": "End-to-End System Evaluation"}
    )
    
    # Print summary
    print("\n📈 Results Summary:")
    for metric, scores in results.items():
        if isinstance(scores, dict) and "mean" in scores:
            print(f"  {metric}: {scores['mean']:.2%}")
    
    return results


# =============================================================================
# Main Evaluation Runner
# =============================================================================

@weave.op()
async def run_all_evaluations():
    """
    Run all agent evaluations.
    
    Returns:
        Dictionary with all evaluation results
    """
    print("\n" + "="*70)
    print("🎯 eSIM Agent Demo - Comprehensive Evaluation")
    print("="*70)
    print(f"\n📡 Weave Project: {project_name}")
    print(f"🔗 View results at: https://wandb.ai/{project_name.replace('/', '/projects/')}/weave")
    
    results = {}
    
    # Evaluate Plan Search Agent
    try:
        results["plan_search"] = await evaluate_plan_search_agent()
    except Exception as e:
        print(f"\n❌ Plan Search evaluation failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Evaluate RAG Agent
    try:
        results["rag"] = await evaluate_rag_agent()
    except Exception as e:
        print(f"\n❌ RAG evaluation failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Evaluate Booking Agent
    try:
        results["booking"] = await evaluate_booking_agent()
    except Exception as e:
        print(f"\n❌ Booking evaluation failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Evaluate End-to-End System
    try:
        results["end_to_end"] = await evaluate_end_to_end_system()
    except Exception as e:
        print(f"\n❌ End-to-End evaluation failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Final summary
    print("\n" + "="*70)
    print("✅ Evaluation Complete!")
    print("="*70)
    print(f"\n🔗 View detailed results at:")
    print(f"   https://wandb.ai/{project_name.replace('/', '/projects/')}/weave")
    print("\n" + "="*70)
    
    return results


async def run_single_evaluation(agent_type: str):
    """
    Run evaluation for a single agent type.
    
    Args:
        agent_type: One of 'plan_search', 'rag', 'booking', or 'end_to_end'
    """
    if agent_type == "plan_search":
        return await evaluate_plan_search_agent()
    elif agent_type == "rag":
        return await evaluate_rag_agent()
    elif agent_type == "booking":
        return await evaluate_booking_agent()
    elif agent_type == "end_to_end":
        return await evaluate_end_to_end_system()
    else:
        raise ValueError(f"Unknown agent type: {agent_type}. Valid options: plan_search, rag, booking, end_to_end")


# =============================================================================
# CLI Entry Point
# =============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Run specific agent evaluation
        agent_type = sys.argv[1]
        print(f"Running evaluation for: {agent_type}")
        asyncio.run(run_single_evaluation(agent_type))
    else:
        # Run all evaluations
        asyncio.run(run_all_evaluations())

