"""
Configuration module for API keys and environment variables.
Load API keys from environment variables for security.
"""

import os
from typing import Optional

def get_openai_api_key() -> Optional[str]:
    """
    Get OpenAI API key from environment variable.
    Set the OPENAI_API_KEY environment variable before running the application.
    """
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("WARNING: OPENAI_API_KEY environment variable not set.")
        print("To set it, run: export OPENAI_API_KEY='your-api-key-here'")
    return api_key

def get_groq_api_key() -> Optional[str]:
    """
    Get Groq API key from environment variable.
    Set the GROQ_API_KEY environment variable before running the application.
    """
    return os.getenv('GROQ_API_KEY')

# Example usage:
# from config import get_openai_api_key
# api_key = get_openai_api_key()
# if api_key:
#     client = OpenAI(api_key=api_key)