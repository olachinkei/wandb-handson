"""
Booking Agent Scorers

Scorers for evaluating Booking Agent responses.
Includes both exact match and LLM-as-a-judge scorers.
"""

import weave
import json
from openai import OpenAI
from typing import List, Optional
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


class BookingToolAccuracyScorer(weave.Scorer):
    """
    Evaluates if the correct tools were called for booking.
    """
    
    @weave.op
    def score(self, model_output: dict, expected_tool_calls: List[str]) -> dict:
        """
        Check if expected tools were called.
        
        Args:
            model_output: Agent output dictionary
            expected_tool_calls: List of expected tool names
        """
        called_tools = model_output.get("tool_calls", [])
        
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


class BookingFlowCompletionScorer(weave.Scorer):
    """
    Checks if the booking flow was completed correctly.
    """
    
    @weave.op
    def score(
        self, 
        model_output: dict,
        expected_ready_to_book: bool,
        expected_prompt_login: bool = False,
        expected_prompt_payment: bool = False
    ) -> dict:
        """
        Check if booking flow completed correctly.
        
        Args:
            model_output: Agent output dictionary
            expected_ready_to_book: Whether user should be ready to book
            expected_prompt_login: Whether login prompt is expected
            expected_prompt_payment: Whether payment method prompt is expected
        """
        output = model_output.get("output", model_output.get("final_output", ""))
        if isinstance(output, dict):
            output = str(output)
        
        output_lower = output.lower()
        
        if expected_ready_to_book:
            # Should show confirmation or completion
            completion_indicators = [
                "confirm", "total", "tax", "purchase complete",
                "booking confirmed", "order placed", "ready to book"
            ]
            completed = any(indicator in output_lower for indicator in completion_indicators)
            
            return {
                "booking_flow_completion": completed,
                "status": "completed" if completed else "incomplete"
            }
        else:
            # Should prompt for login or payment
            login_indicators = ["log in", "login", "sign in", "not logged in", "please log in"]
            payment_indicators = ["payment method", "add a payment", "credit card", "payment information"]
            
            has_login_prompt = any(indicator in output_lower for indicator in login_indicators)
            has_payment_prompt = any(indicator in output_lower for indicator in payment_indicators)
            
            # Check if prompts match expectations
            correct_prompt = False
            if expected_prompt_login and has_login_prompt:
                correct_prompt = True
            elif expected_prompt_payment and has_payment_prompt:
                correct_prompt = True
            elif not expected_prompt_login and not expected_prompt_payment and (has_login_prompt or has_payment_prompt):
                correct_prompt = True
            
            return {
                "booking_flow_completion": correct_prompt,
                "status": "correctly_prompted" if correct_prompt else "missing_prompt"
            }


class BookingAccuracyScorer(LLMJudgeScorer):
    """
    Evaluates cost calculation accuracy using LLM judge.
    """
    
    @weave.op
    def score(
        self, 
        model_output: dict,
        plan_price: float,
        quantity: int,
        expected_total: Optional[float] = None
    ) -> dict:
        """
        Judge booking cost calculation accuracy.
        
        Args:
            model_output: Agent output dictionary
            plan_price: Plan price (None for ambiguous cases)
            quantity: Quantity ordered (None for ambiguous cases)
            expected_total: Expected total with tax (optional for non-booking scenarios)
        """
        output = model_output.get("output", model_output.get("final_output", ""))
        if isinstance(output, dict):
            output = str(output)
        
        # Handle ambiguous cases where plan details are None
        if plan_price is None or quantity is None:
            # Ambiguous case - agent should ask for clarification
            return {
                "accuracy": None,  # Not applicable for ambiguous cases
                "scenario": "ambiguous_input"
            }
        
        # If no expected_total, this is a scenario where user can't book
        # Just check for appropriate messaging
        if expected_total is None:
            login_payment_indicators = [
                "log in", "login", "sign in", "payment method",
                "add a payment", "credit card"
            ]
            has_appropriate_message = any(
                indicator in output.lower() 
                for indicator in login_payment_indicators
            )
            
            return {
                "accuracy": has_appropriate_message,
                "scenario": "no_booking_expected"
            }
        
        system_prompt = """You are evaluating if a booking agent calculated costs correctly.

Check if:
1. The total cost is correct (price × quantity + 8% tax)
2. The total is clearly presented to the user

Respond with a JSON object:
{
    "costs_correct": true/false,
    "explanation": "Brief explanation"
}"""
        
        user_prompt = f"""Plan Price: ${plan_price}
Quantity: {quantity}
Expected Total (with 8% tax): ${expected_total}

Agent Output:
{output}

Evaluate cost calculation accuracy:"""
        
        judgment = self.call_llm_judge(system_prompt, user_prompt)
        
        try:
            result = json.loads(judgment)
            return {
                "accuracy": result.get("costs_correct", False),
                "explanation": result.get("explanation", "")
            }
        except json.JSONDecodeError:
            # Fallback: check if expected total appears in output
            expected_total_str = f"{expected_total:.2f}"
            total_appears = expected_total_str in output
            
            return {
                "accuracy": total_appears,
                "explanation": "JSON parse failed, checked for total in output"
            }


# Scorer list for Booking Agent
BOOKING_SCORERS = [
    BookingToolAccuracyScorer(),
    BookingFlowCompletionScorer(),
    BookingAccuracyScorer(),
    ClarificationScorer(),
    ClarificationAppropriatenessScorer(),
]

