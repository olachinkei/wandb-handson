"""
Configuration file and LLM client loader

You can switch between OpenAI/Gemini in config.yaml.
"""

import os
from pathlib import Path
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
    return {"provider": "openai", "default_vendor": "openai"}


def get_default_vendor() -> str:
    """Get default LLM vendor from config."""
    config = load_config()
    return config.get("provider", "openai")


def get_llm_client():
    """Get the LLM client based on config."""
    config = load_config()
    provider = config.get("provider", "openai")
    
    if provider == "openai":
        import openai
        return openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    elif provider == "gemini":
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        return genai
    else:
        raise ValueError(f"Unknown provider: {provider}")


def get_model_name() -> str:
    """Get the model name based on config."""
    config = load_config()
    provider = config.get("provider", "openai")
    
    if provider == "openai":
        return config.get("openai", {}).get("model", "gpt-4o-mini")
    elif provider == "gemini":
        return config.get("gemini", {}).get("model", "gemini-1.5-flash")
    else:
        return "gpt-4o-mini"


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
    Unified chat completion function that works with both OpenAI and Gemini.
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        temperature: Optional temperature override
        max_tokens: Optional max_tokens override
    
    Returns:
        Response text
    """
    config = load_config()
    provider = config.get("provider", "openai")
    temp = temperature if temperature is not None else get_temperature()
    tokens = max_tokens if max_tokens is not None else get_max_tokens()
    
    if provider == "openai":
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model=get_model_name(),
            messages=messages,
            temperature=temp,
            max_tokens=tokens,
        )
        return response.choices[0].message.content
    
    elif provider == "gemini":
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel(get_model_name())
        
        # Convert messages to Gemini format
        prompt_parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                prompt_parts.append(f"System: {content}\n")
            elif role == "user":
                prompt_parts.append(f"User: {content}\n")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}\n")
        
        response = model.generate_content(
            "".join(prompt_parts),
            generation_config=genai.types.GenerationConfig(
                temperature=temp,
                max_output_tokens=tokens,
            )
        )
        return response.text
    
    else:
        raise ValueError(f"Unknown provider: {provider}")
