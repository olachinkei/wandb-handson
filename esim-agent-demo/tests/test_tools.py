"""
Unit tests for agent tools.
"""

import pytest
from src.tools import (
    ask_country_period_impl,
    plan_search_impl,
    status_check_impl,
    cost_calculator_impl,
)


class TestPlanSearchTools:
    """Test plan search tools."""
    
    def test_ask_country_period_with_dates(self):
        """Test country period with start and end dates."""
        result = ask_country_period_impl(
            countries="Japan, South Korea",
            start_date="2025-01-01",
            end_date="2025-01-08"
        )
        
        assert "countries" in result
        assert len(result["countries"]) == 2
        assert "Japan" in result["countries"]
        assert "South Korea" in result["countries"]
        assert result["requested_days"] == 7
        assert result["plan_duration"] == 7
    
    def test_ask_country_period_with_days(self):
        """Test country period with number of days."""
        result = ask_country_period_impl(
            countries="France",
            days=10
        )
        
        assert result["countries"] == ["France"]
        assert result["requested_days"] == 10
        assert result["plan_duration"] == 15  # Rounds up to next available
    
    def test_ask_country_period_invalid_dates(self):
        """Test invalid date format."""
        result = ask_country_period_impl(
            countries="Japan",
            start_date="01-01-2025",  # Wrong format
            end_date="01-08-2025"
        )
        
        assert "error" in result
    
    def test_plan_search_single_country(self):
        """Test plan search for single country."""
        result = plan_search_impl(
            countries=["Japan"],
            days=7
        )
        
        assert "plans" in result
        assert len(result["plans"]) >= 1
        
        # Should have at least local plan
        local_plans = [p for p in result["plans"] if p["type"] == "local"]
        assert len(local_plans) >= 1
        
        plan = local_plans[0]
        assert plan["days"] == 7
        assert "price" in plan
        assert "data_gb" in plan
    
    def test_plan_search_regional(self):
        """Test plan search for multiple countries in same region."""
        result = plan_search_impl(
            countries=["France", "Germany"],
            days=15
        )
        
        assert "plans" in result
        assert len(result["plans"]) >= 1
        
        # Should suggest regional plan
        regional_plans = [p for p in result["plans"] if p["type"] == "regional"]
        assert len(regional_plans) >= 1
    
    def test_plan_search_global(self):
        """Test plan search for cross-regional countries."""
        result = plan_search_impl(
            countries=["Japan", "United States", "France"],
            days=30
        )
        
        assert "plans" in result
        # Should suggest global plan for cross-regional
        global_plans = [p for p in result["plans"] if p["type"] == "global"]
        assert len(global_plans) >= 1


class TestBookingTools:
    """Test booking tools."""
    
    def test_status_check_logged_in_with_payment(self):
        """Test status check for user with login and payment."""
        result = status_check_impl(user_id="user_001")
        
        assert result["user_id"] == "user_001"
        assert result["is_logged_in"] is True
        assert result["has_payment_method"] is True
        assert result["ready_to_book"] is True
        assert "user_name" in result
    
    def test_status_check_no_payment(self):
        """Test status check for user without payment method."""
        result = status_check_impl(user_id="user_002")
        
        assert result["is_logged_in"] is True
        assert result["has_payment_method"] is False
        assert result["ready_to_book"] is False
    
    def test_status_check_not_logged_in(self):
        """Test status check for logged out user."""
        result = status_check_impl(user_id="user_003")
        
        assert result["is_logged_in"] is False
        assert result["ready_to_book"] is False
    
    def test_cost_calculator_single_plan(self):
        """Test cost calculation for single plan."""
        result = cost_calculator_impl(plan_price=19.99, quantity=1)
        
        assert result["quantity"] == 1
        assert "subtotal" in result
        assert "tax" in result
        assert "total" in result
        assert result["total_value"] > 19.99  # Should include tax
    
    def test_cost_calculator_multiple_plans(self):
        """Test cost calculation for multiple plans."""
        result = cost_calculator_impl(plan_price=10.00, quantity=3)
        
        assert result["quantity"] == 3
        # Subtotal should be 30.00
        assert result["total_value"] > 30.00  # Should include tax
        assert "tax_rate" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

