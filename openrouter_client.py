# openrouter_client.py
"""
OpenRouter API Client for LLM completions.
Uses environment variables for configuration.
"""

import os
import requests
import time
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class OpenRouterClient:
    """Client for interacting with OpenRouter API."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: str = "https://openrouter.ai/api/v1"
    ):
        """
        Initialize OpenRouter client.
        
        Args:
            api_key: OpenRouter API key (defaults to env var OPENROUTER_API_KEY)
            model: Model to use (defaults to env var or llama-3.1-8b-instruct:free)
            base_url: OpenRouter API base URL
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key is required. "
                "Set OPENROUTER_API_KEY in .env file or pass api_key parameter."
            )
        
        # Use free Llama model as default (best free option on OpenRouter)
        self.model = model or os.getenv(
            "OPENROUTER_MODEL", 
            "meta-llama/llama-3.1-8b-instruct:free"
        )
        self.base_url = base_url
        self.chat_endpoint = f"{base_url}/chat/completions"
    
    def chat_completion(
        self,
        messages: list[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ) -> Optional[str]:
        """
        Get chat completion from OpenRouter.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens in response
            max_retries: Number of retry attempts on failure
            retry_delay: Seconds to wait between retries
            
        Returns:
            Generated text response or None on failure
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8501",  # For OpenRouter analytics
            "X-Title": "SQL Multi-Agent System"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        for attempt in range(max_retries):
            try:
                print(f"[OpenRouter] Calling API with model: {self.model}")
                response = requests.post(
                    self.chat_endpoint,
                    json=payload,
                    headers=headers,
                    timeout=30
                )
                
                print(f"[OpenRouter] Response status: {response.status_code}")
                
                response.raise_for_status()
                
                data = response.json()
                
                # Extract content from response
                if "choices" in data and len(data["choices"]) > 0:
                    content = data["choices"][0]["message"]["content"]
                    print(f"[OpenRouter] Success! Response length: {len(content)} chars")
                    return content
                else:
                    print(f"[OpenRouter] Unexpected response format: {data}")
                    return None
                    
            except requests.exceptions.HTTPError as e:
                print(f"[OpenRouter] HTTP Error (attempt {attempt + 1}/{max_retries}): {e}")
                if response.text:
                    print(f"[OpenRouter] Response body: {response.text[:500]}")
                
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    print("[OpenRouter] Max retries reached. Request failed.")
                    return None
                    
            except requests.exceptions.RequestException as e:
                print(f"[OpenRouter] Request failed (attempt {attempt + 1}/{max_retries}): {e}")
                
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    print("[OpenRouter] Max retries reached. Request failed.")
                    return None
            
            except Exception as e:
                print(f"[OpenRouter] Unexpected error: {e}")
                return None
        
        return None
    
    def test_connection(self) -> bool:
        """
        Test if API connection works.
        
        Returns:
            True if connection successful, False otherwise
        """
        test_messages = [
            {"role": "user", "content": "Say 'OK' if you can read this."}
        ]
        
        response = self.chat_completion(
            messages=test_messages,
            temperature=0.0,
            max_tokens=10
        )
        
        return response is not None


# Singleton instance for reuse across agents
_client_instance: Optional[OpenRouterClient] = None


def get_openrouter_client() -> OpenRouterClient:
    """Get or create singleton OpenRouter client instance."""
    global _client_instance
    if _client_instance is None:
        _client_instance = OpenRouterClient()
    return _client_instance
