import asyncio
from typing import Any, Callable, List, Optional, Tuple

import weave
from agents import Agent, Runner, set_trace_processors
from pydantic import Field
from weave.integrations.openai_agents.openai_agents import WeaveTracingProcessor
set_trace_processors([WeaveTracingProcessor()])

import config
from eval_utils import (
    CLAIMS_AGENT_TESTS,
    FAQ_AGENT_TESTS,
    FLIGHT_AGENT_TESTS,
    HOTEL_AGENT_TESTS,
    MULTI_AGENT_TESTS,
    ExpectedBehavior,
    create_agents,
)

weave.init(config.WEAVE_PROJECT)


@weave.op()
def evaluate_final_output(
    expected_validator: Callable[[str], bool], model_output: dict
) -> dict:
    """Evaluate if the final output matches expected criteria"""
    is_correct = expected_validator(model_output["final_output"])
    return {"correct": is_correct, "score": float(is_correct)}


@weave.op()
def evaluate_tool_calls(expected_tools: List[str], model_output: dict) -> dict:
    """Evaluate if the correct tools were called"""
    actual_tool_calls = []
    for item in model_output["new_items"]:
        if hasattr(item, "type") and item.type == "tool_call_item":
            if hasattr(item, "raw_item"):
                tool_name = item.raw_item.name
                actual_tool_calls.append(tool_name)

    correct = all(
        any(expected_tool.lower() == actual.lower() for actual in actual_tool_calls)
        for expected_tool in expected_tools
    )
    return {
        "correct": correct,
        "score": float(correct),
        "actual_calls": actual_tool_calls,
    }


@weave.op()
def evaluate_agent_routing(expected_sequence: List[str], model_output: dict) -> dict:
    """Evaluate if agents were routed correctly"""
    if len(expected_sequence) == 1:
        correct = expected_sequence[0] == model_output["last_agent"].name
    else:
        correct = model_output["last_agent"].name == expected_sequence[-1]

    return {
        "correct": correct,
        "score": float(correct),
        "final_agent": model_output["last_agent"].name,
    }


@weave.op()
def evaluate_step_count(min_steps: int, max_steps: int, model_output: dict) -> dict:
    """Evaluate if the number of steps is appropriate"""
    step_count = len(model_output["new_items"])
    correct = min_steps <= step_count <= max_steps
    return {"correct": correct, "score": float(correct), "step_count": step_count}


class AgentModel(weave.Model):
    name: Optional[str] = None
    agent: Any = Field(default=None)

    def __init__(self, agent: Agent, name: str = None):
        super().__init__()  # Important: call weave.Model's __init__
        self.agent = agent
        self.name = name if name else agent.name

    @weave.op()
    async def predict(self, prompt: str) -> dict:
        result = await Runner.run(self.agent, prompt)
        return {
            "final_output": result.final_output,
            "new_items": result.new_items,
            "last_agent": result.last_agent,
            "raw_responses": result.raw_responses,
        }


def create_evaluation_dataset(tests: List[Tuple[str, ExpectedBehavior]]) -> List[dict]:
    return [
        {
            "prompt": prompt,
            "expected_validator": expected.final_output_validator,
            "expected_tools": expected.expected_tool_calls,
            "expected_sequence": expected.expected_agent_sequence,
            "min_steps": expected.min_steps,
            "max_steps": expected.max_steps,
        }
        for prompt, expected in tests
    ]


async def evaluate_agent_with_weave(
    agent: Agent, tests: List[Tuple[str, ExpectedBehavior]], agent_name: str
):
    model = AgentModel(agent)
    dataset = create_evaluation_dataset(tests)

    # Create descriptive display names
    if agent_name.startswith("Triage_Agent_"):
        # For multi-agent tests, use the category name
        category = agent_name.replace("Triage_Agent_", "")
        display_name = f"Multi-Agent System - {category} Scenarios"
    else:
        # For individual agents, describe their role
        display_names = {
            "Flight_Booking_Agent": "Flight Booking - Direct Reservations",
            "Hotel_Booking_Agent": "Hotel Booking - Accommodation Requests",
            "Claims_Agent": "Claims Processing - Customer Support",
            "FAQ_Agent": "FAQ Service - Information Queries",
        }
        display_name = display_names.get(agent_name, agent_name)

    evaluation = weave.Evaluation(
        name=f"{agent_name}_evaluation",
        dataset=dataset,
        scorers=[
            evaluate_final_output,
            evaluate_tool_calls,
            evaluate_agent_routing,
            evaluate_step_count,
        ],
    )

    return await evaluation.evaluate(model, __weave={"display_name": display_name})


@weave.op()
async def multi_agent_evals():
    # Test both instruction styles
    for style in ["standard", "enhanced"]:
        (
            flight_agent,
            hotel_agent,
            claims_agent,
            faq_agent,
            booking_router_agent,
            triage_agent,
        ) = create_agents(style)

        display_style = "Standard" if style == "standard" else "Enhanced Service"

        # Individual agent evaluations
        individual_results = {
            f"Flight Booking Agent ({display_style})": await evaluate_agent_with_weave(
                flight_agent, FLIGHT_AGENT_TESTS, f"Flight_Booking_Agent_{style}"
            ),
            f"Hotel Booking Agent ({display_style})": await evaluate_agent_with_weave(
                hotel_agent, HOTEL_AGENT_TESTS, f"Hotel_Booking_Agent_{style}"
            ),
            f"Claims Agent ({display_style})": await evaluate_agent_with_weave(
                claims_agent, CLAIMS_AGENT_TESTS, f"Claims_Agent_{style}"
            ),
            f"FAQ Agent ({display_style})": await evaluate_agent_with_weave(
                faq_agent, FAQ_AGENT_TESTS, f"FAQ_Agent_{style}"
            ),
        }

        # Multi-agent system evaluations
        multi_agent_results = {}
        for category, tests in MULTI_AGENT_TESTS.items():
            multi_agent_results[f"{category} ({display_style})"] = (
                await evaluate_agent_with_weave(
                    triage_agent, tests, f"Triage_Agent_{category}_{style}"
                )
            )

        # Print summary
        print("\n=== Evaluation Results ===")

        print("\nIndividual Agent Scores:")
        for agent_name, results in individual_results.items():
            print(f"{agent_name}:")
            print(
                f"  Final Output Score: {results['evaluate_final_output']['score']['mean']:.2%}"
            )
            print(
                f"  Tool Calls Score: {results['evaluate_tool_calls']['score']['mean']:.2%}"
            )
            print(
                f"  Agent Routing Score: {results['evaluate_agent_routing']['score']['mean']:.2%}"
            )
            print(
                f"  Step Count Score: {results['evaluate_step_count']['score']['mean']:.2%}"
            )

        print("\nMulti-agent System Scores:")
        for category, results in multi_agent_results.items():
            print(f"{category}:")
            print(
                f"  Final Output Score: {results['evaluate_final_output']['score']['mean']:.2%}"
            )
            print(
                f"  Tool Calls Score: {results['evaluate_tool_calls']['score']['mean']:.2%}"
            )
            print(
                f"  Agent Routing Score: {results['evaluate_agent_routing']['score']['mean']:.2%}"
            )
            print(
                f"  Step Count Score: {results['evaluate_step_count']['score']['mean']:.2%}"
            )


if __name__ == "__main__":
    asyncio.run(multi_agent_evals())
