"""
Unit tests for evaluation infrastructure.
"""

import pytest
import json
from pathlib import Path

from evaluation.eval import (
    load_scenarios,
    prepare_plan_search_dataset,
    prepare_rag_dataset,
    prepare_booking_dataset,
    prepare_multi_agent_dataset,
)
from evaluation.scorers_plan_search import PLAN_SEARCH_SCORERS
from evaluation.scorers_rag import RAG_SCORERS
from evaluation.scorers_booking import BOOKING_SCORERS
from evaluation.scorers_multi_agent import MULTI_AGENT_SCORERS


class TestScenarioLoading:
    """Test scenario loading functions."""
    
    def test_load_plan_search_scenarios(self):
        """Test loading plan search scenarios."""
        scenarios = load_scenarios("plan_search_scenarios.json")
        
        assert len(scenarios) > 0
        assert isinstance(scenarios, list)
        
        # Check first scenario structure
        scenario = scenarios[0]
        assert "id" in scenario
        assert "input" in scenario
        assert "expected_tool_calls" in scenario
        assert "expected_countries" in scenario
        assert "expected_days" in scenario
        assert "expected_plan_type" in scenario
    
    def test_load_rag_scenarios(self):
        """Test loading RAG scenarios."""
        scenarios = load_scenarios("rag_scenarios.json")
        
        assert len(scenarios) > 0
        assert isinstance(scenarios, list)
        
        # Check first scenario structure
        scenario = scenarios[0]
        assert "id" in scenario
        assert "input" in scenario
    
    def test_load_booking_scenarios(self):
        """Test loading booking scenarios."""
        scenarios = load_scenarios("booking_scenarios.json")
        
        assert len(scenarios) > 0
        assert isinstance(scenarios, list)
        
        # Check first scenario structure
        scenario = scenarios[0]
        assert "id" in scenario
        assert "input" in scenario
        assert "expected_tool_calls" in scenario


class TestDatasetPreparation:
    """Test dataset preparation functions."""
    
    def test_prepare_plan_search_dataset(self):
        """Test Plan Search dataset preparation."""
        dataset = prepare_plan_search_dataset()
        
        assert len(dataset) > 0
        assert isinstance(dataset, list)
        
        # Check first item
        item = dataset[0]
        assert "input" in item
        assert "expected_tool_calls" in item
        assert "expected_countries" in item
        assert "expected_days" in item
        assert "id" in item
    
    def test_prepare_rag_dataset(self):
        """Test RAG dataset preparation."""
        dataset = prepare_rag_dataset()
        
        assert len(dataset) > 0
        assert isinstance(dataset, list)
        
        # Check first item
        item = dataset[0]
        assert "input" in item
        assert "id" in item
    
    def test_prepare_booking_dataset(self):
        """Test Booking dataset preparation."""
        dataset = prepare_booking_dataset()
        
        assert len(dataset) > 0
        assert isinstance(dataset, list)
        
        # Check first item
        item = dataset[0]
        assert "input" in item
        assert "expected_tool_calls" in item
        assert "id" in item
    
    def test_load_multi_agent_scenarios(self):
        """Test loading multi-agent scenarios."""
        scenarios = load_scenarios("multi_agent_scenarios.json")
        
        assert len(scenarios) > 0
        assert isinstance(scenarios, list)
        
        # Check first scenario structure
        scenario = scenarios[0]
        assert "id" in scenario
        assert "input" in scenario
        assert "expected_agent_sequence" in scenario
        assert "expected_tools" in scenario
        assert "intermediate_checks" in scenario
        assert "final_checks" in scenario
    
    def test_prepare_multi_agent_dataset(self):
        """Test Multi-Agent dataset preparation."""
        dataset = prepare_multi_agent_dataset()
        
        assert len(dataset) > 0
        assert isinstance(dataset, list)
        
        # Check first item
        item = dataset[0]
        assert "input" in item
        assert "expected_agent_sequence" in item
        assert "expected_tools" in item
        assert "intermediate_checks" in item
        assert "final_checks" in item
        assert "expected_step_range" in item
        assert "id" in item


class TestScorerConfiguration:
    """Test scorer configuration."""
    
    def test_plan_search_scorers_exist(self):
        """Test Plan Search scorers are configured."""
        assert len(PLAN_SEARCH_SCORERS) > 0
        
        # Check scorer types
        scorer_names = [type(scorer).__name__ for scorer in PLAN_SEARCH_SCORERS]
        assert "PlanSearchToolAccuracyScorer" in scorer_names
        assert "PlanSearchAccuracyScorer" in scorer_names
        assert "PlanSearchBookingPromptScorer" in scorer_names
    
    def test_rag_scorers_exist(self):
        """Test RAG scorers are configured."""
        assert len(RAG_SCORERS) > 0
        
        # Check scorer types
        scorer_names = [type(scorer).__name__ for scorer in RAG_SCORERS]
        assert "RAGFaithfulnessScorer" in scorer_names
        assert "RAGAnswerRelevancyScorer" in scorer_names
        assert "RAGAccuracyScorer" in scorer_names
    
    def test_booking_scorers_exist(self):
        """Test Booking scorers are configured."""
        assert len(BOOKING_SCORERS) > 0
        
        # Check scorer types
        scorer_names = [type(scorer).__name__ for scorer in BOOKING_SCORERS]
        assert "BookingToolAccuracyScorer" in scorer_names
        assert "BookingFlowCompletionScorer" in scorer_names
        assert "BookingAccuracyScorer" in scorer_names
    
    def test_multi_agent_scorers_exist(self):
        """Test Multi-Agent scorers are configured."""
        assert len(MULTI_AGENT_SCORERS) > 0
        
        # Check scorer types
        scorer_names = [type(scorer).__name__ for scorer in MULTI_AGENT_SCORERS]
        assert "MultiAgentSequenceScorer" in scorer_names
        assert "MultiAgentToolUsageScorer" in scorer_names
        assert "MultiAgentFinalAccuracyScorer" in scorer_names
        assert "MultiAgentStepCountScorer" in scorer_names
        assert "MultiAgentReflectionDetectionScorer" in scorer_names
        assert "MultiAgentOverallSuccessScorer" in scorer_names


class TestScenarioValidity:
    """Test scenario data validity."""
    
    def test_plan_search_scenarios_have_expected_fields(self):
        """Test all plan search scenarios have required fields."""
        scenarios = load_scenarios("plan_search_scenarios.json")
        
        required_fields = [
            "id", "input", "expected_tool_calls", "expected_countries",
            "expected_days", "expected_plan_type", "description"
        ]
        
        for scenario in scenarios:
            for field in required_fields:
                assert field in scenario, f"Scenario {scenario['id']} missing field: {field}"
    
    def test_rag_scenarios_have_expected_fields(self):
        """Test all RAG scenarios have required fields."""
        scenarios = load_scenarios("rag_scenarios.json")
        
        required_fields = ["id", "input", "description"]
        
        for scenario in scenarios:
            for field in required_fields:
                assert field in scenario, f"Scenario {scenario['id']} missing field: {field}"
    
    def test_booking_scenarios_have_expected_fields(self):
        """Test all booking scenarios have required fields."""
        scenarios = load_scenarios("booking_scenarios.json")
        
        required_fields = [
            "id", "input", "user_id", "plan_price", "quantity",
            "expected_tool_calls", "description"
        ]
        
        for scenario in scenarios:
            for field in required_fields:
                assert field in scenario, f"Scenario {scenario['id']} missing field: {field}"
    
    def test_multi_agent_scenarios_have_expected_fields(self):
        """Test all multi-agent scenarios have required fields."""
        scenarios = load_scenarios("multi_agent_scenarios.json")
        
        required_fields = [
            "id", "input", "user_id", "expected_agent_sequence",
            "expected_tools", "intermediate_checks", "final_checks",
            "expected_step_range", "description"
        ]
        
        for scenario in scenarios:
            for field in required_fields:
                assert field in scenario, f"Scenario {scenario['id']} missing field: {field}"


class TestScenarioCounts:
    """Test scenario counts match documentation."""
    
    def test_plan_search_scenario_count(self):
        """Test Plan Search has 8 scenarios (5 positive + 2 negative + 1 ambiguous)."""
        scenarios = load_scenarios("plan_search_scenarios.json")
        assert len(scenarios) == 8, f"Expected 8 scenarios, got {len(scenarios)}"
    
    def test_rag_scenario_count(self):
        """Test RAG has 8 scenarios."""
        scenarios = load_scenarios("rag_scenarios.json")
        assert len(scenarios) == 8, f"Expected 8 scenarios, got {len(scenarios)}"
    
    def test_booking_scenario_count(self):
        """Test Booking has 6 scenarios (5 positive + 1 ambiguous)."""
        scenarios = load_scenarios("booking_scenarios.json")
        assert len(scenarios) == 6, f"Expected 6 scenarios, got {len(scenarios)}"
    
    def test_multi_agent_scenario_count(self):
        """Test Multi-Agent has 15 scenarios (8 plan_search + 4 rag + 3 booking)."""
        scenarios = load_scenarios("multi_agent_scenarios.json")
        assert len(scenarios) == 15, f"Expected 15 scenarios, got {len(scenarios)}"
    
    def test_total_scenario_count(self):
        """Test total scenario count is 37 (8 plan_search + 8 rag + 6 booking + 15 multi_agent)."""
        plan_search = load_scenarios("plan_search_scenarios.json")
        rag = load_scenarios("rag_scenarios.json")
        booking = load_scenarios("booking_scenarios.json")
        multi_agent = load_scenarios("multi_agent_scenarios.json")
        
        total = len(plan_search) + len(rag) + len(booking) + len(multi_agent)
        assert total == 37, f"Expected 37 total scenarios, got {total}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

