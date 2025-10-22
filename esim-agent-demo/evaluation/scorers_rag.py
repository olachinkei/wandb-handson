"""
RAG Agent Scorers

Scorers for evaluating RAG (Retrieval-Augmented Generation) Agent responses.
Includes both exact match and LLM-as-a-judge scorers.
"""

import weave
from openai import OpenAI
from typing import Optional
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


class RAGFaithfulnessScorer(LLMJudgeScorer):
    """
    Evaluates if the response is faithful to the retrieved knowledge.
    Uses LLM-as-a-judge.
    """
    
    @weave.op
    def score(self, model_output: dict, input: str) -> dict:
        """
        Check faithfulness using LLM judge.
        
        Args:
            model_output: Agent output dictionary
            input: Original user question
        """
        output = model_output.get("output", model_output.get("final_output", ""))
        if isinstance(output, dict):
            output = str(output)
        
        system_prompt = """You are an expert judge evaluating the faithfulness of AI responses.
Faithfulness means the response is grounded in the retrieved information and doesn't make up facts.

Score the response as:
- FAITHFUL: Response is well-grounded in retrieved information
- UNFAITHFUL: Response contains hallucinations or unsupported claims
- UNCLEAR: Cannot determine faithfulness

Respond with only: FAITHFUL, UNFAITHFUL, or UNCLEAR"""

        user_prompt = f"""Question: {input}

Response to evaluate:
{output}

Is this response faithful (grounded in factual information about eSIMs)?"""

        judgment = self.call_llm_judge(system_prompt, user_prompt)
        
        is_faithful = "FAITHFUL" in judgment.upper()
        
        return {
            "faithfulness": is_faithful,
            "judgment": judgment
        }
    
    def summarize(self, score_rows: list) -> dict:
        """Summarize faithfulness scores."""
        valid_rows = [row for row in score_rows if row.get("faithfulness") is not None]
        total_samples = len(valid_rows)
        
        if total_samples == 0:
            return {"faithfulness": 0.0}
        
        true_count = sum(1 for row in valid_rows if row.get("faithfulness"))
        return {"faithfulness": true_count / total_samples}


class RAGAnswerRelevancyScorer(LLMJudgeScorer):
    """
    Evaluates if the answer is relevant to the question.
    Uses LLM-as-a-judge.
    """
    
    @weave.op
    def score(self, model_output: dict, input: str) -> dict:
        """
        Check answer relevancy using LLM judge.
        
        Args:
            model_output: Agent output dictionary
            input: Original user question
        """
        output = model_output.get("output", model_output.get("final_output", ""))
        if isinstance(output, dict):
            output = str(output)
        
        system_prompt = """You are an expert judge evaluating answer relevancy.
A relevant answer directly addresses the user's question.

Score the response as:
- RELEVANT: Directly answers the question
- PARTIALLY_RELEVANT: Addresses some aspects but misses key points
- NOT_RELEVANT: Does not address the question

Respond with only: RELEVANT, PARTIALLY_RELEVANT, or NOT_RELEVANT"""

        user_prompt = f"""Question: {input}

Response to evaluate:
{output}

Is this response relevant to the question?"""

        judgment = self.call_llm_judge(system_prompt, user_prompt)
        
        is_relevant = "RELEVANT" in judgment.upper() and "NOT_RELEVANT" not in judgment.upper()
        
        return {
            "answer_relevancy": is_relevant,
            "judgment": judgment
        }
    
    def summarize(self, score_rows: list) -> dict:
        """Summarize answer relevancy scores."""
        valid_rows = [row for row in score_rows if row.get("answer_relevancy") is not None]
        total_samples = len(valid_rows)
        
        if total_samples == 0:
            return {"answer_relevancy": 0.0}
        
        true_count = sum(1 for row in valid_rows if row.get("answer_relevancy"))
        return {"answer_relevancy": true_count / total_samples}


class RAGSourceCitationScorer(weave.Scorer):
    """
    Checks if the response includes source citations.
    """
    
    @weave.op
    def score(self, model_output: dict) -> dict:
        """
        Check if output cites sources.
        
        Args:
            model_output: Agent output dictionary or string
        """
        # Handle different input types
        if isinstance(model_output, dict):
            output = model_output.get("output", model_output.get("final_output", ""))
        else:
            # If model_output is already a string (or BoxedStr)
            output = str(model_output)
        
        if isinstance(output, dict):
            output = str(output)
        
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
    
    def summarize(self, score_rows: list) -> dict:
        """Summarize source citation scores."""
        valid_rows = [row for row in score_rows if row.get("source_citation") is not None]
        total_samples = len(valid_rows)
        
        if total_samples == 0:
            return {"source_citation": 0.0}
        
        true_count = sum(1 for row in valid_rows if row.get("source_citation"))
        return {"source_citation": true_count / total_samples}


class RAGOutOfScopeHandlingScorer(weave.Scorer):
    """
    Evaluates how well the agent handles out-of-scope questions.
    """
    
    @weave.op
    def score(
        self, 
        model_output: dict,
        expected_out_of_scope: bool,
        expected_redirect: Optional[str] = None
    ) -> dict:
        """
        Check out-of-scope handling.
        
        Args:
            model_output: Agent output dictionary
            expected_out_of_scope: Whether question should be out of scope
            expected_redirect: Expected agent to redirect to
        """
        output = model_output.get("output", model_output.get("final_output", ""))
        if isinstance(output, dict):
            output = str(output)
        
        output_lower = output.lower()
        
        if not expected_out_of_scope:
            # Question is in scope, should answer directly
            redirect_phrases = [
                "plan search agent", "booking agent",
                "connect you with", "redirect", "transfer"
            ]
            incorrectly_redirected = any(phrase in output_lower for phrase in redirect_phrases)
            
            return {
                "out_of_scope_handling": not incorrectly_redirected,
                "correct_behavior": "answered_directly" if not incorrectly_redirected else "incorrectly_redirected"
            }
        else:
            # Question is out of scope, should redirect
            if expected_redirect:
                redirect_found = expected_redirect.lower() in output_lower
            else:
                redirect_phrases = ["plan search", "booking", "connect you", "redirect"]
                redirect_found = any(phrase in output_lower for phrase in redirect_phrases)
            
            return {
                "out_of_scope_handling": redirect_found,
                "correct_behavior": "redirected" if redirect_found else "failed_to_redirect"
            }
    
    def summarize(self, score_rows: list) -> dict:
        """Summarize out-of-scope handling scores."""
        valid_rows = [row for row in score_rows if row.get("out_of_scope_handling") is not None]
        total_samples = len(valid_rows)
        
        if total_samples == 0:
            return {"out_of_scope_handling": 0.0}
        
        true_count = sum(1 for row in valid_rows if row.get("out_of_scope_handling"))
        return {"out_of_scope_handling": true_count / total_samples}


class RAGAccuracyScorer(LLMJudgeScorer):
    """
    Overall accuracy scorer for RAG responses.
    Uses LLM-as-a-judge to evaluate if the answer is correct.
    """
    
    @weave.op
    def score(
        self,
        model_output: dict,
        input: str,
        expected_topics: Optional[list] = None
    ) -> dict:
        """
        Check overall accuracy using LLM judge.
        
        Args:
            model_output: Agent output dictionary
            input: Original user question
            expected_topics: List of topics that should be covered
        """
        output = model_output.get("output", model_output.get("final_output", ""))
        if isinstance(output, dict):
            output = str(output)
        
        system_prompt = """You are an expert judge evaluating eSIM-related answers for accuracy.
Evaluate if the answer correctly addresses the question about eSIMs.

Score the response as:
- ACCURATE: Answer is correct and complete
- PARTIALLY_ACCURATE: Answer is mostly correct but has minor issues
- INACCURATE: Answer contains significant errors or is wrong

Respond with only: ACCURATE, PARTIALLY_ACCURATE, or INACCURATE"""

        topics_info = ""
        if expected_topics:
            topics_info = f"\n\nExpected topics to cover: {', '.join(expected_topics)}"
        
        user_prompt = f"""Question: {input}{topics_info}

Response to evaluate:
{output}

Is this answer accurate?"""

        judgment = self.call_llm_judge(system_prompt, user_prompt)
        
        is_accurate = "ACCURATE" in judgment.upper() and "INACCURATE" not in judgment.upper()
        
        return {
            "accuracy": is_accurate,
            "judgment": judgment
        }
    
    def summarize(self, score_rows: list) -> dict:
        """Summarize accuracy scores."""
        valid_rows = [row for row in score_rows if row.get("accuracy") is not None]
        total_samples = len(valid_rows)
        
        if total_samples == 0:
            return {"accuracy": 0.0}
        
        true_count = sum(1 for row in valid_rows if row.get("accuracy"))
        return {"accuracy": true_count / total_samples}


# Scorer list for RAG Agent
RAG_SCORERS = [
    RAGFaithfulnessScorer(),
    RAGAnswerRelevancyScorer(),
    RAGSourceCitationScorer(),
    RAGOutOfScopeHandlingScorer(),
    RAGAccuracyScorer(),
    ClarificationScorer(),
    ClarificationAppropriatenessScorer(),
]

