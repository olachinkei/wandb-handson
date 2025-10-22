"""
Evaluation Scorers for eSIM Agent Demo

Based on Weave documentation:
- https://weave-docs.wandb.ai/guides/evaluation/scorers
- https://weave-docs.wandb.ai/guides/evaluation/builtin_scorers
- https://weave-docs.wandb.ai/guides/evaluation/weave_local_scorers
"""

import weave
from openai import OpenAI
from typing import Dict, Any, List, Optional
import os


# =============================================================================
# Base LLM Judge Scorer
# =============================================================================

class LLMJudgeScorer(weave.Scorer):
    """
    Base scorer that uses LLM as a judge for evaluating responses.
    """
    model_id: str = "gpt-4o-mini"
    
    @weave.op
    def get_client(self) -> OpenAI:
        """Get OpenAI client (created lazily)."""
        return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    @weave.op
    def call_llm_judge(self, system_prompt: str, user_prompt: str) -> dict:
        """Call LLM to judge the response."""
        client = self.get_client()
        response = client.chat.completions.create(
            model=self.model_id,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0
        )
        
        content = response.choices[0].message.content
        return {"raw_judgment": content}


# =============================================================================
# Common Scorers (used across all agents)
# =============================================================================

class ClarificationScorer(LLMJudgeScorer):
    """
    Evaluates if the agent provides a complete answer or fails to do so.
    Distinguishes between asking clarifying questions and providing incomplete answers.
    Uses LLM as a judge.
    """
    
    @weave.op
    def score(self, model_output: dict) -> dict:
        """
        Evaluate answer completeness.
        
        Args:
            model_output: Agent output dictionary
        """
        output = model_output.get("output", model_output.get("final_output", ""))
        if isinstance(output, dict):
            output = str(output)
        
        system_prompt = """You are evaluating an AI agent's response quality.

Analyze the agent's output and categorize it:

1. COMPLETE_ANSWER: The agent provided a complete, helpful response
   - Shows plan details with prices
   - Explains eSIM information clearly
   - Completes a booking with total cost
   - Provides troubleshooting steps

2. ASKING_CLARIFICATION: The agent asks for more information
   - Asks "What country?", "When?", "How long?"
   - Says "I need more information"
   - Requests missing details to proceed

3. INCOMPLETE_ANSWER: The agent fails to provide useful information
   - Says "I don't know" or "I can't help"
   - Provides vague or unhelpful responses
   - Doesn't use available tools/knowledge
   - Gives partial information without completion

Note: Asking "Would you like to book?" AFTER showing results is COMPLETE_ANSWER.

Respond with ONLY one of: "COMPLETE_ANSWER", "ASKING_CLARIFICATION", or "INCOMPLETE_ANSWER"."""

        user_prompt = f"""Agent Output:
{output}

Categorize this response:"""
        
        judgment = self.call_llm_judge(system_prompt, user_prompt)
        response_type = judgment.get("raw_judgment", "").strip().upper()
        
        is_complete = response_type == "COMPLETE_ANSWER"
        is_asking = response_type == "ASKING_CLARIFICATION"
        is_incomplete = response_type == "INCOMPLETE_ANSWER"
        
        return {
            "provides_complete_answer": is_complete,
            "is_asking_clarification": is_asking,
            "has_incomplete_answer": is_incomplete,
            "response_type": response_type
        }
    
    def summarize(self, score_rows: list) -> dict:
        """Summarize clarification scores - just counts for each category."""
        complete_count = sum(1 for row in score_rows if row.get("provides_complete_answer"))
        asking_count = sum(1 for row in score_rows if row.get("is_asking_clarification"))
        incomplete_count = sum(1 for row in score_rows if row.get("has_incomplete_answer"))
        
        return {
            "provides_complete_answer_count": complete_count,
            "is_asking_clarification_count": asking_count,
            "has_incomplete_answer_count": incomplete_count
        }


class ClarificationAppropriatenessScorer(LLMJudgeScorer):
    """
    Evaluates if asking for clarification is appropriate given the input.
    
    - If input is ambiguous: asking clarification is CORRECT
    - If input is clear: asking clarification is INCORRECT (unnecessary)
    - Complete answer is always good
    - Incomplete answer is always bad
    """
    
    @weave.op
    def score(self, is_ambiguous: bool, model_output: dict) -> dict:
        """
        Evaluate if clarification is appropriate.
        
        Args:
            is_ambiguous: Whether the input is ambiguous
            model_output: Agent output
        """
        # Extract output
        output = model_output.get("output", model_output.get("final_output", ""))
        if isinstance(output, dict):
            output = str(output)
        
        # Use LLM to classify response type
        system_prompt = """You are evaluating an AI agent's response.

Categorize the response:

1. COMPLETE_ANSWER: Agent provided a complete, helpful response
2. ASKING_CLARIFICATION: Agent asks for more information
3. INCOMPLETE_ANSWER: Agent fails to provide useful information

Respond with ONLY one of: "COMPLETE_ANSWER", "ASKING_CLARIFICATION", or "INCOMPLETE_ANSWER"."""

        user_prompt = f"""Agent Output:
{output}

Categorize:"""
        
        judgment = self.call_llm_judge(system_prompt, user_prompt)
        response_type = judgment.get("raw_judgment", "").strip().upper()
        
        is_asking = response_type == "ASKING_CLARIFICATION"
        is_complete = response_type == "COMPLETE_ANSWER"
        is_incomplete = response_type == "INCOMPLETE_ANSWER"
        
        # Evaluate appropriateness
        if is_complete:
            # Complete answer is always good
            appropriate = True
            reason = "Provided complete answer"
        elif is_incomplete:
            # Incomplete answer is always bad
            appropriate = False
            reason = "Failed to provide useful information"
        elif is_asking:
            if is_ambiguous:
                # Asking for clarification on ambiguous input = GOOD
                appropriate = True
                reason = "Correctly asked for clarification on ambiguous input"
            else:
                # Asking for clarification on clear input = BAD
                appropriate = False
                reason = "Unnecessarily asked for clarification on clear input"
        else:
            # Unknown response type
            appropriate = False
            reason = "Unknown response type"
        
        return {
            "clarification_appropriate": appropriate,
            "clarification_reason": reason,
            "is_ambiguous_input": is_ambiguous,
            "agent_asked_clarification": is_asking
        }
    
    def summarize(self, score_rows: list) -> dict:
        """Summarize clarification appropriateness scores."""
        valid_rows = [row for row in score_rows if row.get("clarification_appropriate") is not None]
        total_samples = len(valid_rows)
        
        if total_samples == 0:
            return {"clarification_appropriate": 0.0}
        
        true_count = sum(1 for row in valid_rows if row.get("clarification_appropriate"))
        return {"clarification_appropriate": true_count / total_samples}


# =============================================================================
# Plan Search Agent Scorers
# =============================================================================

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


class PlanSearchAccuracyScorer(LLMJudgeScorer):
    """
    Uses LLM to judge if the plan search results are accurate.
    Evaluates date calculation and pricing accuracy together.
    """
    
    @weave.op
    def score(
        self, 
        model_output: dict,
        expected_countries: List[str],
        expected_days: int,
        expected_plan_type: str
    ) -> dict:
        """
        Judge if plan search is accurate.
        
        Args:
            model_output: Agent output dictionary
            expected_countries: Expected countries list
            expected_days: Expected number of days
            expected_plan_type: Expected plan type (local/regional/global)
        """
        # Extract output and input
        output = model_output.get("output", model_output.get("final_output", ""))
        
        system_prompt = """You are evaluating an eSIM plan search agent's accuracy.
        
Your task is to determine if the agent:
1. Correctly identified the countries from user input
2. Correctly calculated the number of days
3. Suggested the appropriate plan type (local/regional/global)
4. Provided accurate pricing information

Respond with a JSON object:
{
    "countries_correct": true/false,
    "days_correct": true/false,
    "plan_type_correct": true/false,
    "overall_accurate": true/false,
    "explanation": "Brief explanation of your judgment"
}"""
        
        user_prompt = f"""User Input: {input}

Expected:
- Countries: {', '.join(expected_countries)}
- Days: {expected_days}
- Plan Type: {expected_plan_type}

Agent Output:
{output}

Evaluate the accuracy:"""
        
        judgment = self.call_llm_judge(system_prompt, user_prompt)
        
        # Parse JSON from judgment
        import json
        try:
            result = json.loads(judgment["raw_judgment"])
            return {
                "accuracy": result.get("overall_accurate", False),
                "countries_correct": result.get("countries_correct", False),
                "days_correct": result.get("days_correct", False),
                "plan_type_correct": result.get("plan_type_correct", False),
                "explanation": result.get("explanation", "")
            }
        except json.JSONDecodeError:
            return {
                "accuracy": False,
                "error": "Failed to parse LLM judgment",
                "raw": judgment["raw_judgment"]
            }


class PlanSearchBookingPromptScorer(weave.Scorer):
    """
    Checks if the agent prompts the user to proceed with booking.
    """
    
    @weave.op
    def score(self, model_output: dict) -> dict:
        """
        Check if output contains booking prompt.
        
        Args:
            model_output: Agent output dictionary with 'output' key
        """
        # Extract output string
        output = model_output.get("output", model_output.get("final_output", ""))
        if isinstance(output, dict):
            output = str(output)
        
        # Look for booking-related keywords
        booking_keywords = [
            "book", "purchase", "buy", "proceed", "order",
            "would you like to", "ready to", "shall we"
        ]
        
        output_lower = output.lower()
        has_prompt = any(keyword in output_lower for keyword in booking_keywords)
        
        return {
            "booking_prompt_present": has_prompt
        }


# =============================================================================
# RAG Agent Scorers
# =============================================================================

class RAGFaithfulnessScorer(LLMJudgeScorer):
    """
    Evaluates if the response is faithful to the source material.
    """
    
    @weave.op
    def score(self, model_output: dict) -> dict:
        """
        Judge faithfulness of RAG response.
        
        Args:
            model_output: Agent output dictionary
        """
        # Extract output
        output = model_output.get("output", model_output.get("final_output", ""))
        
        system_prompt = """You are evaluating if an AI response is faithful to its source material.

A response is faithful if it:
1. Does not make up information not in the sources
2. Accurately represents the source content
3. Does not contradict the sources

Respond with a JSON object:
{
    "faithful": true/false,
    "explanation": "Brief explanation"
}"""
        
        user_prompt = f"""Response:
{output}

Is this response faithful to source material (no hallucinations)?"""
        
        judgment = self.call_llm_judge(system_prompt, user_prompt)
        
        import json
        try:
            result = json.loads(judgment["raw_judgment"])
            return {
                "faithfulness": result.get("faithful", False),
                "explanation": result.get("explanation", "")
            }
        except json.JSONDecodeError:
            return {
                "faithfulness": False,
                "error": "Failed to parse judgment"
            }


class RAGAnswerRelevancyScorer(LLMJudgeScorer):
    """
    Evaluates if the answer is relevant to the question.
    """
    
    @weave.op
    def score(self, output: str, input: str) -> dict:
        """
        Judge answer relevancy.
        
        Args:
            output: Agent's response
            input: User's question
        """
        system_prompt = """You are evaluating if an AI response is relevant to the user's question.

A relevant response:
1. Directly addresses the question asked
2. Provides useful information related to the query
3. Doesn't go off-topic

Respond with a JSON object:
{
    "relevant": true/false,
    "relevancy_score": 0-5 (0=not relevant, 5=highly relevant),
    "explanation": "Brief explanation"
}"""
        
        user_prompt = f"""Question: {input}

Response:
{output}

Evaluate relevancy:"""
        
        judgment = self.call_llm_judge(system_prompt, user_prompt)
        
        import json
        try:
            result = json.loads(judgment["raw_judgment"])
            return {
                "answer_relevancy": result.get("relevant", False),
                "relevancy_score": result.get("relevancy_score", 0),
                "explanation": result.get("explanation", "")
            }
        except json.JSONDecodeError:
            return {
                "answer_relevancy": False,
                "error": "Failed to parse judgment"
            }


class RAGSourceCitationScorer(weave.Scorer):
    """
    Checks if the response includes source citations.
    """
    
    @weave.op
    def score(self, output: str) -> dict:
        """
        Check if output cites sources.
        
        Args:
            output: Agent's response
        """
        # Look for citation indicators
        citation_indicators = [
            "according to", "source:", "based on",
            "[", "【", "reference", "documentation"
        ]
        
        output_lower = output.lower()
        has_citation = any(indicator in output_lower for indicator in citation_indicators)
        
        return {
            "source_citation": has_citation
        }


class RAGOutOfScopeHandlingScorer(weave.Scorer):
    """
    Evaluates how well the agent handles out-of-scope questions.
    """
    
    @weave.op
    def score(
        self, 
        output: str, 
        expected_out_of_scope: bool,
        expected_redirect: Optional[str] = None
    ) -> dict:
        """
        Check out-of-scope handling.
        
        Args:
            output: Agent's response
            expected_out_of_scope: Whether question should be out of scope
            expected_redirect: Expected agent to redirect to
        """
        if not expected_out_of_scope:
            # Question is in scope, should answer directly
            redirect_phrases = [
                "plan search agent", "booking agent",
                "connect you with", "redirect", "transfer"
            ]
            output_lower = output.lower()
            incorrectly_redirected = any(phrase in output_lower for phrase in redirect_phrases)
            
            return {
                "out_of_scope_handling": not incorrectly_redirected,
                "correct_behavior": "answered_directly" if not incorrectly_redirected else "incorrectly_redirected"
            }
        else:
            # Question is out of scope, should redirect
            output_lower = output.lower()
            
            if expected_redirect:
                redirect_found = expected_redirect.lower() in output_lower
            else:
                redirect_phrases = ["plan search", "booking", "connect you", "redirect"]
                redirect_found = any(phrase in output_lower for phrase in redirect_phrases)
            
            return {
                "out_of_scope_handling": redirect_found,
                "correct_behavior": "redirected" if redirect_found else "failed_to_redirect"
            }


class RAGAccuracyScorer(LLMJudgeScorer):
    """
    Overall accuracy scorer for RAG responses.
    """
    
    @weave.op
    def score(self, output: str, input: str, expected_topics: List[str]) -> dict:
        """
        Judge overall accuracy of RAG response.
        
        Args:
            output: Agent's response
            input: User's question
            expected_topics: Topics that should be covered
        """
        system_prompt = """You are evaluating the accuracy of an eSIM knowledge base response.

Check if the response:
1. Accurately answers the question
2. Covers the expected topics
3. Provides correct technical information

Respond with a JSON object:
{
    "accurate": true/false,
    "topics_covered": ["topic1", "topic2"],
    "explanation": "Brief explanation"
}"""
        
        user_prompt = f"""Question: {input}

Expected Topics: {', '.join(expected_topics)}

Response:
{output}

Evaluate accuracy:"""
        
        judgment = self.call_llm_judge(system_prompt, user_prompt)
        
        import json
        try:
            result = json.loads(judgment["raw_judgment"])
            return {
                "accuracy": result.get("accurate", False),
                "topics_covered": result.get("topics_covered", []),
                "explanation": result.get("explanation", "")
            }
        except json.JSONDecodeError:
            return {
                "accuracy": False,
                "error": "Failed to parse judgment"
            }


# =============================================================================
# Booking Agent Scorers
# =============================================================================

class BookingToolAccuracyScorer(weave.Scorer):
    """
    Evaluates if the correct tools were called for booking.
    """
    
    @weave.op
    def score(self, output: dict, expected_tool_calls: List[str]) -> dict:
        """
        Check if expected tools were called.
        
        Args:
            output: Agent output containing tool call information
            expected_tool_calls: List of expected tool names
        """
        called_tools = output.get("tool_calls", [])
        
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
        output: str,
        expected_ready_to_book: bool
    ) -> dict:
        """
        Check if booking flow completed correctly.
        
        Args:
            output: Agent's response
            expected_ready_to_book: Whether user should be ready to book
        """
        output_lower = output.lower()
        
        if expected_ready_to_book:
            # Should show confirmation or completion
            completion_indicators = [
                "confirm", "total", "tax", "purchase complete",
                "booking confirmed", "order placed"
            ]
            completed = any(indicator in output_lower for indicator in completion_indicators)
            
            return {
                "booking_flow_completion": completed,
                "status": "completed" if completed else "incomplete"
            }
        else:
            # Should prompt for login or payment
            prompt_indicators = [
                "log in", "login", "sign in", "payment method",
                "add a payment", "credit card"
            ]
            prompted = any(indicator in output_lower for indicator in prompt_indicators)
            
            return {
                "booking_flow_completion": prompted,
                "status": "correctly_prompted" if prompted else "missing_prompt"
            }


class BookingAccuracyScorer(LLMJudgeScorer):
    """
    Evaluates cost calculation accuracy using LLM judge.
    """
    
    @weave.op
    def score(
        self, 
        output: str,
        plan_price: float,
        quantity: int,
        expected_total: float
    ) -> dict:
        """
        Judge booking cost calculation accuracy.
        
        Args:
            output: Agent's response
            plan_price: Plan price
            quantity: Quantity ordered
            expected_total: Expected total with tax
        """
        system_prompt = """You are evaluating if a booking agent calculated costs correctly.

Check if:
1. The subtotal is correct (price × quantity)
2. Tax is calculated correctly (8%)
3. The total is correct (subtotal + tax)
4. All costs are clearly presented

Respond with a JSON object:
{
    "costs_correct": true/false,
    "subtotal_shown": true/false,
    "tax_shown": true/false,
    "total_shown": true/false,
    "explanation": "Brief explanation"
}"""
        
        user_prompt = f"""Plan Price: ${plan_price}
Quantity: {quantity}
Expected Total (with 8% tax): ${expected_total}

Agent Output:
{output}

Evaluate cost calculation accuracy:"""
        
        judgment = self.call_llm_judge(system_prompt, user_prompt)
        
        import json
        try:
            result = json.loads(judgment["raw_judgment"])
            return {
                "accuracy": result.get("costs_correct", False),
                "subtotal_shown": result.get("subtotal_shown", False),
                "tax_shown": result.get("tax_shown", False),
                "total_shown": result.get("total_shown", False),
                "explanation": result.get("explanation", "")
            }
        except json.JSONDecodeError:
            return {
                "accuracy": False,
                "error": "Failed to parse judgment"
            }


# =============================================================================
# Scorer Lists for Each Agent
# =============================================================================

PLAN_SEARCH_SCORERS = [
    PlanSearchToolAccuracyScorer(),
    PlanSearchAccuracyScorer(),
    PlanSearchBookingPromptScorer(),
]

RAG_SCORERS = [
    RAGFaithfulnessScorer(),
    RAGAnswerRelevancyScorer(),
    RAGSourceCitationScorer(),
    RAGOutOfScopeHandlingScorer(),
    RAGAccuracyScorer(),
]

BOOKING_SCORERS = [
    BookingToolAccuracyScorer(),
    BookingFlowCompletionScorer(),
    BookingAccuracyScorer(),
]

