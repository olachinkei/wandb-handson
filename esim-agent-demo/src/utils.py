"""
Utility functions for eSIM Agent Demo.

This module provides configuration loading, file operations, and helper functions.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


def get_project_root() -> Path:
    """
    Get the project root directory.
    
    Returns:
        Path: Project root directory path
    """
    return Path(__file__).parent.parent


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Optional path to config file. If None, uses default location.
        
    Returns:
        Dict containing configuration
        
    Raises:
        FileNotFoundError: If config file not found
        yaml.YAMLError: If config file is invalid
    """
    if config_path is None:
        config_path = get_project_root() / "config" / "config.yaml"
    else:
        config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Validate required fields
    required_fields = ['weave', 'agents', 'rag']
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Missing required configuration field: {field}")
    
    return config


def load_json(file_path: str | Path) -> Dict[str, Any]:
    """
    Load JSON file.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Dict containing JSON data
        
    Raises:
        FileNotFoundError: If file not found
        json.JSONDecodeError: If file is invalid JSON
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data


def save_json(data: Dict[str, Any], file_path: str | Path, indent: int = 2) -> None:
    """
    Save data to JSON file.
    
    Args:
        data: Data to save
        file_path: Path to JSON file
        indent: JSON indentation (default: 2)
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def load_price_list() -> Dict[str, Any]:
    """
    Load eSIM pricing database.
    
    Returns:
        Dict containing pricing data with 'local', 'regional', and 'global' plans
    """
    config = load_config()
    price_list_path = get_project_root() / config['tools']['plan_search']['database_path']
    return load_json(price_list_path)


def load_user_cache() -> Dict[str, Any]:
    """
    Load mock user cache data.
    
    Returns:
        Dict containing user session data
    """
    config = load_config()
    cache_path = get_project_root() / config['tools']['user_cache']['cache_path']
    return load_json(cache_path)


def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Get user data from cache.
    
    Args:
        user_id: User ID to lookup
        
    Returns:
        User data dict or None if not found
    """
    cache = load_user_cache()
    return cache.get('users', {}).get(user_id)


def check_user_login(user_id: str) -> bool:
    """
    Check if user is logged in.
    
    Args:
        user_id: User ID to check
        
    Returns:
        True if user is logged in, False otherwise
    """
    user = get_user(user_id)
    if user is None:
        return False
    return user.get('is_logged_in', False)


def check_payment_method(user_id: str) -> bool:
    """
    Check if user has payment method registered.
    
    Args:
        user_id: User ID to check
        
    Returns:
        True if user has payment method, False otherwise
    """
    user = get_user(user_id)
    if user is None:
        return False
    return user.get('has_payment_method', False)


def format_price(amount: float, currency: str = "USD") -> str:
    """
    Format price with currency symbol.
    
    Args:
        amount: Price amount
        currency: Currency code (default: USD)
        
    Returns:
        Formatted price string
    """
    symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'JPY': '¥',
    }
    
    symbol = symbols.get(currency, currency)
    
    if currency == 'JPY':
        # No decimal for Japanese Yen
        return f"{symbol}{int(amount)}"
    else:
        return f"{symbol}{amount:.2f}"


def calculate_days_between_dates(start_date: str, end_date: str) -> int:
    """
    Calculate number of days between two dates.
    
    Args:
        start_date: Start date (YYYY-MM-DD format)
        end_date: End date (YYYY-MM-DD format)
        
    Returns:
        Number of days
        
    Raises:
        ValueError: If date format is invalid
    """
    from datetime import datetime
    
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        delta = end - start
        return max(1, delta.days)  # At least 1 day
    except ValueError as e:
        raise ValueError(f"Invalid date format. Use YYYY-MM-DD. Error: {e}")


def get_closest_plan_duration(days: int) -> int:
    """
    Get closest available plan duration.
    
    Args:
        days: Desired number of days
        
    Returns:
        Closest available plan duration (1, 3, 7, 15, or 30 days)
    """
    available_durations = [1, 3, 7, 15, 30]
    
    # Find closest duration that meets or exceeds the requirement
    for duration in available_durations:
        if duration >= days:
            return duration
    
    # If more than 30 days, return 30 (user can purchase multiple or extend)
    return 30


def setup_logging(config: Optional[Dict[str, Any]] = None) -> None:
    """
    Setup application logging.
    
    Args:
        config: Configuration dict. If None, loads from default location.
    """
    import logging
    import logging.handlers
    
    if config is None:
        config = load_config()
    
    log_config = config.get('app', {}).get('logging', {})
    level = getattr(logging, log_config.get('level', 'INFO'))
    format_str = log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_file = log_config.get('file', 'logs/app.log')
    
    # Create logs directory
    log_path = get_project_root() / log_file
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Setup root logger
    logging.basicConfig(
        level=level,
        format=format_str,
        handlers=[
            logging.StreamHandler(),  # Console
            logging.handlers.RotatingFileHandler(
                log_path,
                maxBytes=log_config.get('max_file_size', 10485760),
                backupCount=log_config.get('backup_count', 5)
            )
        ]
    )


def validate_environment() -> bool:
    """
    Validate that required environment variables are set.
    
    Returns:
        True if all required variables are set, False otherwise
    """
    required_vars = ['OPENAI_API_KEY', 'WANDB_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("\nPlease create a .env file with:")
        for var in missing_vars:
            print(f"  {var}=your_key_here")
        return False
    
    print("✅ All required environment variables are set")
    return True


if __name__ == "__main__":
    """Test configuration loading"""
    print("Testing configuration loading...")
    
    try:
        # Test config loading
        config = load_config()
        print(f"✅ Configuration loaded successfully")
        print(f"   - Weave project: {config['weave']['project']}")
        print(f"   - Main agent model: {config['agents']['esim_agent']['model']}")
        
        # Test environment validation
        print("\nValidating environment...")
        validate_environment()
        
        # Test data loading
        print("\nTesting data loading...")
        price_list = load_price_list()
        print(f"✅ Price list loaded: {len(price_list['local'])} local plans")
        
        user_cache = load_user_cache()
        print(f"✅ User cache loaded: {len(user_cache['users'])} users")
        
        # Test helper functions
        print("\nTesting helper functions...")
        print(f"✅ Format price: {format_price(19.99)}")
        print(f"✅ Days calculation: {calculate_days_between_dates('2025-01-01', '2025-01-08')} days")
        print(f"✅ Closest plan for 10 days: {get_closest_plan_duration(10)} days")
        
        print("\n🎉 All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

