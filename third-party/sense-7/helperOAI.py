#!/usr/bin/env python3
"""
OpenAI API Helper Module

This module provides helper functions for interacting with the standard OpenAI API.

Configuration:
- Set your OpenAI API key in the OPENAI_API_KEY variable below
- Or set it as an environment variable: export OPENAI_API_KEY="your-key-here"
- Adjust other parameters as needed for your setup

"""

import os
import time
from openai import OpenAI

# ====================== CONFIGURATION ======================
# OpenAI API Configuration
# You can set your API key here or use an environment variable
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")  # Set your key here or in environment

# Default model
DEFAULT_MODEL = "gpt-4o"

# Default API parameters
DEFAULT_TEMPERATURE = 0.0
DEFAULT_MAX_TOKENS = 3000
DEFAULT_TOP_P = 1.0
DEFAULT_PRESENCE_PENALTY = 0.0
DEFAULT_FREQUENCY_PENALTY = 0.0

# API endpoint (use default OpenAI endpoint or set custom)
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")  # None uses default OpenAI endpoint
# ===========================================================


def create_client(model: str = DEFAULT_MODEL) -> OpenAI:
    """
    Create and return an OpenAI client instance.
    
    Args:
        model: The model name (not used for client creation, but kept for API compatibility)
    
    Returns:
        OpenAI client instance
    
    Raises:
        ValueError: If API key is not set
    """
    if not OPENAI_API_KEY:
        raise ValueError(
            "OpenAI API key not found. Please set OPENAI_API_KEY in helperOAI.py "
            "or as an environment variable."
        )
    
    # Create client with optional base URL
    client_kwargs = {"api_key": OPENAI_API_KEY}
    if OPENAI_BASE_URL:
        client_kwargs["base_url"] = OPENAI_BASE_URL
    
    client = OpenAI(**client_kwargs)
    print(f"OpenAI client created successfully")
    
    return client


def customCompletion(
    model: str,
    user_input: str,
    start_time: float,
    client: OpenAI = None,
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    top_p: float = DEFAULT_TOP_P,
    presence_penalty: float = DEFAULT_PRESENCE_PENALTY,
    frequency_penalty: float = DEFAULT_FREQUENCY_PENALTY
):
    """
    Make a completion request to OpenAI API.
    
    Args:
        model: Model name (e.g., "gpt-4o", "gpt-4", "gpt-3.5-turbo")
        user_input: The prompt/input text
        start_time: Start time for computing request duration
        client: OpenAI client instance (created if not provided)
        temperature: Sampling temperature (0.0 to 2.0)
        max_tokens: Maximum tokens in response
        top_p: Nucleus sampling parameter
        presence_penalty: Presence penalty (-2.0 to 2.0)
        frequency_penalty: Frequency penalty (-2.0 to 2.0)
    
    Returns:
        tuple: (response_text, request_time, logprobs)
            - response_text: The model's text response
            - request_time: Time taken for the request in seconds
            - logprobs: Log probabilities (None for standard API)
    """
    # Create client if not provided
    if client is None:
        client = create_client(model)
    
    try:
        # Make API call
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant"
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
        )
        
        # Extract response
        response_text = response.choices[0].message.content
        
        # Calculate request time
        end_time = time.time()
        request_time = end_time - start_time
        
        # Note: Standard OpenAI API doesn't return logprobs by default
        # You can request them by adding logprobs=True to the API call if needed
        logprobs = None
        
        return response_text, request_time, logprobs
        
    except Exception as e:
        print(f"Error in OpenAI API call: {e}")
        # Return default values on error
        end_time = time.time()
        request_time = end_time - start_time
        return f"ERROR: {str(e)}", request_time, None


def customCompletion_with_system(
    model: str,
    system_message: str,
    user_input: str,
    start_time: float,
    client: OpenAI = None,
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    top_p: float = DEFAULT_TOP_P,
    presence_penalty: float = DEFAULT_PRESENCE_PENALTY,
    frequency_penalty: float = DEFAULT_FREQUENCY_PENALTY
):
    """
    Make a completion request with a system message.
    
    Args:
        model: Model name
        system_message: System message to set context/behavior
        user_input: The user prompt/input text
        start_time: Start time for computing request duration
        client: OpenAI client instance (created if not provided)
        temperature: Sampling temperature
        max_tokens: Maximum tokens in response
        top_p: Nucleus sampling parameter
        presence_penalty: Presence penalty (-2.0 to 2.0)
        frequency_penalty: Frequency penalty (-2.0 to 2.0)
    
    Returns:
        tuple: (response_text, request_time, logprobs)
    """
    # Create client if not provided
    if client is None:
        client = create_client(model)
    
    try:
        # Make API call with system message
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_input}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
        )
        
        # Extract response
        response_text = response.choices[0].message.content
        
        # Calculate request time
        end_time = time.time()
        request_time = end_time - start_time
        
        logprobs = None
        
        return response_text, request_time, logprobs
        
    except Exception as e:
        print(f"Error in OpenAI API call: {e}")
        end_time = time.time()
        request_time = end_time - start_time
        return f"ERROR: {str(e)}", request_time, None


# Example usage
if __name__ == "__main__":
    """
    Example usage of the OpenAI helper functions.
    Set your OPENAI_API_KEY before running this.
    """
    
    # Check if API key is set
    if not OPENAI_API_KEY:
        print("Please set OPENAI_API_KEY in helperOAI.py or as an environment variable")
        exit(1)
    
    # Create client
    client = create_client(DEFAULT_MODEL)
    
    # Example completion
    start = time.time()
    response, req_time, _ = customCompletion(
        model=DEFAULT_MODEL,
        user_input="What is empathy?",
        start_time=start,
        client=client
    )
    
    print(f"\nResponse: {response}")
    print(f"Request time: {req_time:.2f}s")
