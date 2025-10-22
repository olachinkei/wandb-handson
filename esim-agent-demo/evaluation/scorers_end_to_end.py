"""
End-to-End System Scorers

Scorers for evaluating complete end-to-end workflows across multiple agents.
Evaluates agent handoffs, tool usage, intermediate results, and final outcomes.
"""

import weave
import json
import re
from openai import OpenAI
from typing import List, Dict, Optional, Any
from evaluation.scorers import ClarificationScorer, ClarificationAppropriatenessScorer


class LLMJudgeScorer(weave.Scorer):
    """
    Base class for LLM-as-a-judge scorers.
    """
    
    def get_client(self):
        """Lazy initialization of OpenAI client."""
        return OpenAI()
    
    def call_llm_judge(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = "gpt-4o-mini"
    ) -> str:
        """
        Call LLM to judge the response.
        
        Args:
            system_prompt: System instructions for the judge
            user_prompt: User prompt with content to judge
            model: Model to use for judging
            
        Returns:
            LLM's judgment response
        """
        client = self.get_client()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content


class EndToEndSequenceScorer(weave.Scorer):
    """
    Evaluates if the correct sequence of agents was used.
    """
    
    @weave.op
    def score(
        self, 
        model_output: dict,
        expected_agent_sequence: List[str]
    ) -> dict:
        """
        Check if agents were called in the correct sequence.
        
        Args:
            model_output: Agent output dictionary
            expected_agent_sequence: Expected sequence of agent names
        """
        # Extract agent sequence from new_items
        agent_sequence = []
        if "agent_sequence" in model_output:
            agent_sequence = model_output["agent_sequence"]
        
        # Check if sequence matches
        is_correct = agent_sequence == expected_agent_sequence
        
        # Calculate partial credit
        partial_score = 0.0
        if len(agent_sequence) > 0 and len(expected_agent_sequence) > 0:
            matching_agents = sum(
                1 for a, e in zip(agent_sequence, expected_agent_sequence) if a == e
            )
            partial_score = matching_agents / max(len(agent_sequence), len(expected_agent_sequence))
        
        return {
            "agent_sequence_correct": is_correct,
            "partial_agent_score": partial_score,
            "actual_sequence": " → ".join(agent_sequence) if agent_sequence else "",
            "expected_sequence": " → ".join(expected_agent_sequence) if expected_agent_sequence else ""
        }
    
    def summarize(self, score_rows: list) -> dict:
        """Summarize agent sequence scores."""
        valid_rows = [row for row in score_rows if row.get("agent_sequence_correct") is not None]
        total_samples = len(valid_rows)
        
        if total_samples == 0:
            return {"agent_sequence_correct": {"true_count": 0, "total_samples": 0, "success_rate": 0.0}}
        
        true_count = sum(1 for row in valid_rows if row.get("agent_sequence_correct"))
        return {
            "agent_sequence_correct": {
                "true_count": true_count,
                "total_samples": total_samples,
                "success_rate": true_count / total_samples
            }
        }


class EndToEndToolUsageScorer(weave.Scorer):
    """
    Evaluates if the expected tools were used during the workflow.
    """
    
    @weave.op
    def score(
        self, 
        model_output: dict,
        expected_tools: List[str]
    ) -> dict:
        """
        Check if expected tools were used.
        
        Args:
            model_output: Agent output dictionary
            expected_tools: List of expected tool names
        """
        actual_tools = model_output.get("tool_calls", [])
        
        # Check which expected tools were used
        missing_tools = [tool for tool in expected_tools if tool not in actual_tools]
        extra_tools = [tool for tool in actual_tools if tool not in expected_tools]
        
        is_correct = len(missing_tools) == 0 and len(extra_tools) == 0
        
        return {
            "tool_usage_correct": is_correct,
            "missing_tools": ", ".join(missing_tools) if missing_tools else "",
            "extra_tools": ", ".join(extra_tools) if extra_tools else "",
            "actual_tools": ", ".join(actual_tools) if actual_tools else ""
        }
    
    def summarize(self, score_rows: list) -> dict:
        """Summarize tool usage scores."""
        valid_rows = [row for row in score_rows if row.get("tool_usage_correct") is not None]
        total_samples = len(valid_rows)
        
        if total_samples == 0:
            return {"tool_usage_correct": {"true_count": 0, "total_samples": 0, "success_rate": 0.0}}
        
        true_count = sum(1 for row in valid_rows if row.get("tool_usage_correct"))
        return {
            "tool_usage_correct": {
                "true_count": true_count,
                "total_samples": total_samples,
                "success_rate": true_count / total_samples
            }
        }


class EndToEndFinalAccuracyScorer(LLMJudgeScorer):
    """
    Evaluates final outcome accuracy using LLM as a judge.
    Compares actual output with expected output description.
    """
    
    @weave.op
    def score(
        self, 
        model_output: dict,
        expected_final_output_description: str
    ) -> dict:
        """
        Check if the final output matches the expected description.
        
        Args:
            model_output: Agent output dictionary
            expected_final_output_description: Description of expected final output
        """
        output = model_output.get("output", model_output.get("final_output", ""))
        if isinstance(output, dict):
            output = str(output)
        
        # Use LLM to judge if output matches expected description
        system_prompt = """You are evaluating if an AI agent's output meets the expected requirements.

You will be given:
1. The expected output description (requirements)
2. The actual agent output

Evaluate if the actual output fulfills the requirements described in the expected output.

Consider:
- Does it provide the required information?
- Does it include expected values (prices, countries, dates)?
- Does it complete the expected actions?
- Is the tone and content appropriate?

Respond with a JSON object:
{
  "meets_requirements": true/false,
  "score": 0.0-1.0,
  "reason": "Brief explanation of why it does or doesn't meet requirements"
}"""

        user_prompt = f"""Expected Output Description:
{expected_final_output_description}

Actual Agent Output:
{output}

Does the actual output meet the requirements? Respond with JSON only."""
        
        try:
            judgment_text = self.call_llm_judge(system_prompt, user_prompt)
            # Parse JSON response
            judgment = json.loads(judgment_text)
            
            meets_requirements = judgment.get("meets_requirements", False)
            score = judgment.get("score", 0.0)
            reason = judgment.get("reason", "No reason provided")
            
        except (json.JSONDecodeError, Exception) as e:
            # Fallback if JSON parsing fails
            meets_requirements = False
            score = 0.0
            reason = f"Failed to parse LLM judgment: {str(e)}"
        
        return {
            "final_score": score,
            "meets_requirements": meets_requirements,
            "evaluation_reason": reason
        }
    
    def summarize(self, score_rows: list) -> dict:
        """Summarize final accuracy scores."""
        # For final_score (numerical), calculate average
        valid_scores = [row.get("final_score") for row in score_rows if row.get("final_score") is not None]
        
        # For meets_requirements (boolean), calculate success rate
        valid_meets = [row for row in score_rows if row.get("meets_requirements") is not None]
        
        result = {}
        
        if valid_scores:
            result["final_score"] = {
                "mean": sum(valid_scores) / len(valid_scores),
                "total_samples": len(valid_scores)
            }
        else:
            result["final_score"] = {"mean": 0.0, "total_samples": 0}
        
        if valid_meets:
            true_count = sum(1 for row in valid_meets if row.get("meets_requirements"))
            result["meets_requirements"] = {
                "true_count": true_count,
                "total_samples": len(valid_meets),
                "success_rate": true_count / len(valid_meets)
            }
        else:
            result["meets_requirements"] = {"true_count": 0, "total_samples": 0, "success_rate": 0.0}
        
        return result


class EndToEndStepCountScorer(weave.Scorer):
    """
    Evaluates if the workflow completed within expected step range.
    """
    
    @weave.op
    def score(
        self, 
        model_output: dict,
        expected_step_range: List[int]
    ) -> dict:
        """
        Check if step count is within expected range.
        
        Args:
            model_output: Agent output dictionary
            expected_step_range: [min_steps, max_steps]
        """
        step_count = model_output.get("step_count", 0)
        min_steps, max_steps = expected_step_range
        
        within_range = min_steps <= step_count <= max_steps
        
        # Calculate efficiency score
        if within_range:
            efficiency = 1.0
        else:
            if step_count < min_steps:
                # Too few steps (might be incomplete)
                efficiency = step_count / min_steps
            else:
                # Too many steps (inefficient)
                efficiency = max_steps / step_count
            efficiency = max(0.0, efficiency)
        
        return {
            "step_count_correct": within_range,
            "step_efficiency": efficiency,
            "actual_steps": step_count,
            "expected_range": f"{min_steps}-{max_steps}"
        }
    
    def summarize(self, score_rows: list) -> dict:
        """Summarize step count scores."""
        valid_correct = [row for row in score_rows if row.get("step_count_correct") is not None]
        valid_efficiency = [row.get("step_efficiency") for row in score_rows if row.get("step_efficiency") is not None]
        
        result = {}
        
        if valid_correct:
            true_count = sum(1 for row in valid_correct if row.get("step_count_correct"))
            result["step_count_correct"] = {
                "true_count": true_count,
                "total_samples": len(valid_correct),
                "success_rate": true_count / len(valid_correct)
            }
        else:
            result["step_count_correct"] = {"true_count": 0, "total_samples": 0, "success_rate": 0.0}
        
        if valid_efficiency:
            result["step_efficiency"] = {
                "mean": sum(valid_efficiency) / len(valid_efficiency),
                "total_samples": len(valid_efficiency)
            }
        else:
            result["step_efficiency"] = {"mean": 0.0, "total_samples": 0}
        
        return result


class EndToEndReflectionDetectionScorer(weave.Scorer):
    """
    Detects if the agent performed reflection or error correction.
    """
    
    @weave.op
    def score(self, model_output: dict) -> dict:
        """
        Detect reflection or error correction in the workflow.
        
        Args:
            model_output: Agent output dictionary
        """
        # Check for reflection indicators
        output = model_output.get("output", model_output.get("final_output", ""))
        if isinstance(output, dict):
            output = str(output)
        
        reflection_indicators = [
            "let me try again", "correct", "mistake", "error",
            "sorry", "actually", "revise", "update"
        ]
        
        has_reflection_language = any(
            indicator in output.lower() 
            for indicator in reflection_indicators
        )
        
        # Check tool call patterns for retry behavior
        tool_calls = model_output.get("tool_calls", [])
        has_retry = len(tool_calls) > len(set(tool_calls))
        
        return {
            "reflection_detected": has_reflection_language or has_retry
        }
    
    def summarize(self, score_rows: list) -> dict:
        """Summarize reflection detection scores."""
        valid_rows = [row for row in score_rows if row.get("reflection_detected") is not None]
        total_samples = len(valid_rows)
        
        if total_samples == 0:
            return {"reflection_detected": {"true_count": 0, "total_samples": 0, "success_rate": 0.0}}
        
        true_count = sum(1 for row in valid_rows if row.get("reflection_detected"))
        return {
            "reflection_detected": {
                "true_count": true_count,
                "total_samples": total_samples,
                "success_rate": true_count / total_samples
            }
        }


class EndToEndOverallSuccessScorer(weave.Scorer):
    """
    Overall success evaluation - checks if workflow completed without errors.
    """
    
    @weave.op
    def score(self, model_output: dict) -> dict:
        """
        Evaluate overall success of the multi-agent workflow.
        Simply checks if there were no errors during execution.
        
        Args:
            model_output: Agent output dictionary
        """
        # Check if workflow completed without errors
        has_error = model_output.get("has_error", False)
        
        return {
            "overall_success": not has_error
        }
    
    def summarize(self, score_rows: list) -> dict:
        """Summarize overall success scores."""
        valid_rows = [row for row in score_rows if row.get("overall_success") is not None]
        total_samples = len(valid_rows)
        
        if total_samples == 0:
            return {"overall_success": {"true_count": 0, "total_samples": 0, "success_rate": 0.0}}
        
        true_count = sum(1 for row in valid_rows if row.get("overall_success"))
        return {
            "overall_success": {
                "true_count": true_count,
                "total_samples": total_samples,
                "success_rate": true_count / total_samples
            }
        }


# Scorer list for End-to-End evaluation
END_TO_END_SCORERS = [
    EndToEndSequenceScorer(),
    EndToEndToolUsageScorer(),
    EndToEndFinalAccuracyScorer(),
    EndToEndStepCountScorer(),
    EndToEndReflectionDetectionScorer(),
    EndToEndOverallSuccessScorer(),
    ClarificationScorer(),
    ClarificationAppropriatenessScorer(),
]

