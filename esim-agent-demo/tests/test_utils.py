"""
Unit tests for src/utils.py
"""

import pytest
from pathlib import Path
from src.utils import (
    get_project_root,
    load_config,
    load_json,
    load_price_list,
    load_user_cache,
    get_user,
    check_user_login,
    check_payment_method,
    format_price,
    calculate_days_between_dates,
    get_closest_plan_duration,
)


class TestConfigurationLoading:
    """Test configuration and data loading functions."""
    
    def test_get_project_root(self):
        """Test project root detection."""
        root = get_project_root()
        assert root.exists()
        assert (root / "config" / "config.yaml").exists()
    
    def test_load_config(self):
        """Test configuration loading."""
        config = load_config()
        
        # Check required sections
        assert "weave" in config
        assert "agents" in config
        assert "rag" in config
        
        # Check agent configurations
        assert "esim_agent" in config["agents"]
        assert "plan_search_agent" in config["agents"]
        assert "rag_agent" in config["agents"]
        assert "booking_agent" in config["agents"]
        
        # Check models are specified (latest GPT-5 models)
        assert config["agents"]["esim_agent"]["model"] == "gpt-5-2025-08-07"
        assert config["agents"]["plan_search_agent"]["model"] == "gpt-5-mini-2025-08-07"
    
    def test_load_price_list(self):
        """Test price list loading."""
        price_list = load_price_list()
        
        assert "local" in price_list
        assert "regional" in price_list
        assert "global" in price_list
        
        # Check local plans
        assert len(price_list["local"]) > 0
        assert "Japan" in price_list["local"]
        assert "United States" in price_list["local"]
        
        # Check regional plans
        assert "Europe" in price_list["regional"]
        assert "Asia" in price_list["regional"]
        
        # Validate plan structure
        japan_plans = price_list["local"]["Japan"]["plans"]
        assert len(japan_plans) > 0
        assert "days" in japan_plans[0]
        assert "data_gb" in japan_plans[0]
        assert "price" in japan_plans[0]
    
    def test_load_user_cache(self):
        """Test user cache loading."""
        cache = load_user_cache()
        
        assert "users" in cache
        assert "metadata" in cache
        
        # Check user data
        users = cache["users"]
        assert len(users) > 0
        assert "user_001" in users
        
        # Validate user structure
        user = users["user_001"]
        assert "user_id" in user
        assert "email" in user
        assert "is_logged_in" in user
        assert "has_payment_method" in user


class TestUserFunctions:
    """Test user-related utility functions."""
    
    def test_get_user_exists(self):
        """Test getting existing user."""
        user = get_user("user_001")
        assert user is not None
        assert user["user_id"] == "user_001"
        assert user["email"] == "john.doe@example.com"
    
    def test_get_user_not_exists(self):
        """Test getting non-existent user."""
        user = get_user("user_999")
        assert user is None
    
    def test_check_user_login_true(self):
        """Test checking logged in user."""
        assert check_user_login("user_001") is True
    
    def test_check_user_login_false(self):
        """Test checking logged out user."""
        assert check_user_login("user_003") is False
    
    def test_check_user_login_not_exists(self):
        """Test checking non-existent user login."""
        assert check_user_login("user_999") is False
    
    def test_check_payment_method_true(self):
        """Test checking user with payment method."""
        assert check_payment_method("user_001") is True
    
    def test_check_payment_method_false(self):
        """Test checking user without payment method."""
        assert check_payment_method("user_002") is False
    
    def test_check_payment_method_not_exists(self):
        """Test checking non-existent user payment."""
        assert check_payment_method("user_999") is False


class TestHelperFunctions:
    """Test helper utility functions."""
    
    def test_format_price_usd(self):
        """Test USD price formatting."""
        assert format_price(19.99) == "$19.99"
        assert format_price(100.00) == "$100.00"
        assert format_price(5.5) == "$5.50"
    
    def test_format_price_eur(self):
        """Test EUR price formatting."""
        assert format_price(19.99, "EUR") == "€19.99"
    
    def test_format_price_jpy(self):
        """Test JPY price formatting (no decimals)."""
        assert format_price(1999, "JPY") == "¥1999"
        assert format_price(1999.99, "JPY") == "¥1999"
    
    def test_calculate_days_between_dates(self):
        """Test date calculation."""
        # 1 week
        assert calculate_days_between_dates("2025-01-01", "2025-01-08") == 7
        
        # Same day (minimum 1 day)
        assert calculate_days_between_dates("2025-01-01", "2025-01-01") == 1
        
        # 30 days
        assert calculate_days_between_dates("2025-01-01", "2025-01-31") == 30
    
    def test_calculate_days_invalid_format(self):
        """Test invalid date format handling."""
        with pytest.raises(ValueError):
            calculate_days_between_dates("01-01-2025", "01-08-2025")
        
        with pytest.raises(ValueError):
            calculate_days_between_dates("2025/01/01", "2025/01/08")
    
    def test_get_closest_plan_duration(self):
        """Test closest plan duration matching."""
        # Exact matches
        assert get_closest_plan_duration(1) == 1
        assert get_closest_plan_duration(7) == 7
        assert get_closest_plan_duration(30) == 30
        
        # Round up to next available
        assert get_closest_plan_duration(2) == 3
        assert get_closest_plan_duration(5) == 7
        assert get_closest_plan_duration(10) == 15
        assert get_closest_plan_duration(20) == 30
        
        # More than 30 days caps at 30
        assert get_closest_plan_duration(45) == 30
        assert get_closest_plan_duration(60) == 30


class TestDataValidation:
    """Test data structure validation."""
    
    def test_price_list_has_all_required_fields(self):
        """Validate price list structure."""
        price_list = load_price_list()
        
        # Test a sample local plan
        japan = price_list["local"]["Japan"]
        assert "country_code" in japan
        assert "region" in japan
        assert "plans" in japan
        
        # Test plan structure
        for plan in japan["plans"]:
            assert "days" in plan
            assert "data_gb" in plan
            assert "price" in plan
            assert isinstance(plan["days"], int)
            assert isinstance(plan["data_gb"], (int, float))
            assert isinstance(plan["price"], (int, float))
    
    def test_user_cache_has_valid_users(self):
        """Validate user cache structure."""
        cache = load_user_cache()
        
        for user_id, user in cache["users"].items():
            assert "user_id" in user
            assert "email" in user
            assert "is_logged_in" in user
            assert "has_payment_method" in user
            assert "payment_methods" in user
            assert "purchase_history" in user
            
            # Validate types
            assert isinstance(user["is_logged_in"], bool)
            assert isinstance(user["has_payment_method"], bool)
            assert isinstance(user["payment_methods"], list)
            assert isinstance(user["purchase_history"], list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

