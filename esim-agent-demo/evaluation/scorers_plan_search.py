"""
Plan Search Agent Scorers - Exact Match Based

Using exact match with tool outputs for accuracy verification.
"""

import weave
from typing import List
from evaluation.scorers import ClarificationScorer, ClarificationAppropriatenessScorer


class PlanSearchToolAccuracyScorer(weave.Scorer):
    """
    Evaluates if the correct tools were called for plan search.
    """
    
    @weave.op
    def score(self, model_output: dict, expected_tool_calls: List[str]) -> dict:
        """
        Check if expected tools were called.
        
        Args:
            model_output: Agent output containing tool call information
            expected_tool_calls: List of expected tool names
        """
        # Extract tool calls from output
        called_tools = model_output.get("tool_calls", [])
        
        # Check if all expected tools were called
        missing_tools = []
        for expected_tool in expected_tool_calls:
            if expected_tool not in called_tools:
                missing_tools.append(expected_tool)
        
        is_correct = len(missing_tools) == 0
        
        return {
            "tool_accuracy": is_correct,
            "called_tools": called_tools,
            "missing_tools": missing_tools
        }
    
    def summarize(self, score_rows: list) -> dict:
        """Summarize tool accuracy scores."""
        valid_rows = [row for row in score_rows if row.get("tool_accuracy") is not None]
        total_samples = len(valid_rows)
        
        if total_samples == 0:
            return {"tool_accuracy": {"true_count": 0, "total_samples": 0, "success_rate": 0.0}}
        
        true_count = sum(1 for row in valid_rows if row.get("tool_accuracy"))
        return {
            "tool_accuracy": {
                "true_count": true_count,
                "total_samples": total_samples,
                "success_rate": true_count / total_samples
            }
        }


class PlanSearchAccuracyScorer(weave.Scorer):
    """
    Exact match scorer for plan search accuracy.
    Checks if tool outputs match expected values.
    """
    
    @weave.op
    def score(
        self,
        model_output: dict,
        expected_countries: List[str],
        expected_days: int,
        expected_plan_type: str = None,
        expected_plan_price: float = None
    ) -> dict:
        """
        Check accuracy using exact match on tool outputs.
        
        Args:
            model_output: Agent output dictionary  
            expected_countries: Expected countries (None for ambiguous cases)
            expected_days: Expected days (None for ambiguous cases)
            expected_plan_type: Expected plan type (None if service unavailable or ambiguous)
            expected_plan_price: Expected plan price (None if service unavailable or ambiguous)
        """
        # Handle ambiguous cases where expected values are None
        if expected_countries is None or expected_days is None:
            # Ambiguous case - agent should ask for clarification, not provide plan details
            return {
                "accuracy": None,  # Not applicable for ambiguous cases
                "countries_correct": None,
                "days_correct": None,
                "plan_type_correct": None,
                "price_correct": None
            }
        
        # We'll check if the final output contains the expected values
        output_text = model_output.get("output", model_output.get("final_output", ""))
        if isinstance(output_text, dict):
            output_text = str(output_text)
        output_lower = output_text.lower()
        
        # Check countries (always check for non-ambiguous cases)
        countries_found = all(
            country.lower() in output_lower
            for country in expected_countries
        )
        
        # If plan_type and price are None, this is an unavailable service case
        # Skip checking days, plan_type, and price
        if expected_plan_type is None or expected_plan_price is None:
            return {
                "accuracy": countries_found,  # Only countries matter for unavailable
                "countries_correct": countries_found,
                "days_correct": None,
                "plan_type_correct": None,
                "price_correct": None
            }
        
        # Check days
        days_str = f"{expected_days} day"
        days_found = days_str in output_lower
        
        # Check plan type  
        plan_type_found = expected_plan_type.lower() in output_lower
        
        # Check price (allow some tolerance for formatting)
        price_str = f"${expected_plan_price}"
        price_found = price_str in output_text or f"{expected_plan_price}" in output_text
        
        # Overall accuracy
        accuracy = countries_found and days_found and plan_type_found and price_found
        
        return {
            "accuracy": accuracy,
            "countries_correct": countries_found,
            "days_correct": days_found,
            "plan_type_correct": plan_type_found,
            "price_correct": price_found
        }
    
    def summarize(self, score_rows: list) -> dict:
        """Summarize plan search accuracy scores."""
        valid_rows = [row for row in score_rows if row.get("accuracy") is not None]
        total_samples = len(valid_rows)
        
        if total_samples == 0:
            return {"accuracy": {"true_count": 0, "total_samples": 0, "success_rate": 0.0}}
        
        true_count = sum(1 for row in valid_rows if row.get("accuracy"))
        return {
            "accuracy": {
                "true_count": true_count,
                "total_samples": total_samples,
                "success_rate": true_count / total_samples
            }
        }


class PlanSearchBookingPromptScorer(weave.Scorer):
    """
    Checks if the agent prompts the user to proceed with booking.
    """
    
    @weave.op
    def score(self, model_output: dict, expected_booking_prompt: bool) -> dict:
        """
        Check if output contains booking prompt (or correctly omits it).
        
        Args:
            model_output: Agent output dictionary
            expected_booking_prompt: Whether booking prompt should be present
        """
        output = model_output.get("output", model_output.get("final_output", ""))
        if isinstance(output, dict):
            output = str(output)
        
        booking_keywords = [
            "book", "purchase", "buy", "proceed", "order",
            "would you like to", "ready to", "shall we"
        ]
        
        output_lower = output.lower()
        has_prompt = any(keyword in output_lower for keyword in booking_keywords)
        
        # Check if the actual matches the expected
        is_correct = has_prompt == expected_booking_prompt
        
        return {
            "booking_prompt_present": has_prompt,
            "booking_prompt_correct": is_correct
        }
    
    def summarize(self, score_rows: list) -> dict:
        """Summarize booking prompt scores."""
        valid_rows = [row for row in score_rows if row.get("booking_prompt_correct") is not None]
        total_samples = len(valid_rows)
        
        if total_samples == 0:
            return {"booking_prompt_correct": {"true_count": 0, "total_samples": 0, "success_rate": 0.0}}
        
        true_count = sum(1 for row in valid_rows if row.get("booking_prompt_correct"))
        return {
            "booking_prompt_correct": {
                "true_count": true_count,
                "total_samples": total_samples,
                "success_rate": true_count / total_samples
            }
        }


class PlanSearchServiceAvailabilityScorer(weave.Scorer):
    """
    Checks if the agent correctly handles service unavailability.
    """
    
    @weave.op
    def score(self, model_output: dict, expected_service_available: bool) -> dict:
        """
        Check if service availability is correctly communicated.
        
        Args:
            model_output: Agent output dictionary
            expected_service_available: Whether service should be available
        """
        output = model_output.get("output", model_output.get("final_output", ""))
        if isinstance(output, dict):
            output = str(output)
        
        unavailable_keywords = [
            "not available", "not currently available", "unavailable",
            "do not offer", "don't offer", "cannot provide",
            "not supported", "no plans available"
        ]
        
        output_lower = output.lower()
        has_unavailable_message = any(keyword in output_lower for keyword in unavailable_keywords)
        
        if expected_service_available:
            # Service should be available, so NO unavailable message
            is_correct = not has_unavailable_message
        else:
            # Service should be unavailable, so SHOULD have unavailable message
            is_correct = has_unavailable_message
        
        return {
            "service_availability_correct": is_correct,
            "has_unavailable_message": has_unavailable_message,
            "expected_available": expected_service_available
        }
    
    def summarize(self, score_rows: list) -> dict:
        """Summarize service availability scores."""
        valid_rows = [row for row in score_rows if row.get("service_availability_correct") is not None]
        total_samples = len(valid_rows)
        
        if total_samples == 0:
            return {"service_availability_correct": {"true_count": 0, "total_samples": 0, "success_rate": 0.0}}
        
        true_count = sum(1 for row in valid_rows if row.get("service_availability_correct"))
        return {
            "service_availability_correct": {
                "true_count": true_count,
                "total_samples": total_samples,
                "success_rate": true_count / total_samples
            }
        }


# Scorer list for Plan Search Agent
PLAN_SEARCH_SCORERS = [
    PlanSearchToolAccuracyScorer(),
    PlanSearchAccuracyScorer(),
    PlanSearchBookingPromptScorer(),
    PlanSearchServiceAvailabilityScorer(),
    ClarificationScorer(),
    ClarificationAppropriatenessScorer(),
]
