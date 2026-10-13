"""
Configuration file and OpenAI client loader.
"""

import os
from pathlib import Path

import openai
import yaml
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load config
CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"


def load_config() -> dict:
    """Load configuration from config.yaml."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return yaml.safe_load(f)
    return {"openai": {"model": "gpt-4o-mini"}}


def get_llm_client():
    """Get the OpenAI client."""
    return openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_model_name() -> str:
    """Get the OpenAI model name from config."""
    config = load_config()
    return config.get("openai", {}).get("model", "gpt-4o-mini")


def get_temperature() -> float:
    """Get default temperature."""
    config = load_config()
    return config.get("default_temperature", 0.3)


def get_max_tokens() -> int:
    """Get default max tokens."""
    config = load_config()
    return config.get("default_max_tokens", 150)


def chat_completion(messages: list, temperature: float = None, max_tokens: int = None) -> str:
    """
    OpenAI chat completion helper.

    Args:
        messages: List of message dicts with 'role' and 'content'
        temperature: Optional temperature override
        max_tokens: Optional max_tokens override

    Returns:
        Response text
    """
    temp = temperature if temperature is not None else get_temperature()
    tokens = max_tokens if max_tokens is not None else get_max_tokens()

    response = get_llm_client().chat.completions.create(
        model=get_model_name(),
        messages=messages,
        temperature=temp,
        max_tokens=tokens,
    )
    return response.choices[0].message.content
