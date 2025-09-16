"""
Model provider module for OpenAI integration.
"""

import json
import logging
import time
from typing import Dict, List, Optional, Union

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import (
    OPENAI_MODEL_ENDPOINT,
    OPENAI_MODEL,
    OPENAI_PORT,
    TIMEOUT_SECONDS,
)

logger = logging.getLogger(__name__)


class ModelProvider:
    """Handles communication with OpenAI API."""
    
    def __init__(self):
        """Initialize the model provider with retry logic."""
        self.endpoint = OPENAI_MODEL_ENDPOINT
        self.model_name = OPENAI_MODEL
        self.session = self._create_session()
        self._verify_connection()
    
    def _create_session(self) -> requests.Session:
        """
        Create HTTP session with retry logic.
        Configure the session to automatically retry failed requests (up to 3 times).
        HTTP status codes to retry on:
        429: Too Many Requests
        500: Internal Server Error
        502: Bad Gateway
        503: Service Unavailable
        504: Gateway Timeout
        """
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
    
    def _verify_connection(self):
        """Verify OpenAI backend is running and responsive."""
        try:
            # Send a minimal test request to the backend
            test_payload = {
                "message": "Hello",
                "temperature": 0.0,
                "max_tokens": 5,
                "session_id": "test_session"
            }
            response = self.session.post(
                f"{self.endpoint}/chat",
                json=test_payload,
                timeout=5
            )
            response.raise_for_status()
            
            data = response.json()
            if "response" not in data:
                raise RuntimeError("Unexpected response structure from OpenAI backend.")
            logger.info(f"Successfully connected to OpenAI backend at {self.endpoint}")
            
        except requests.exceptions.ConnectionError:
            raise RuntimeError(
                "Cannot connect to OpenAI backend. Please ensure:\n"
                "1. Backend is running\n"
                "2. Port {OPENAI_PORT} is not blocked"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to verify OpenAI connection: {e}")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None,
        **kwargs
    ) -> Dict:
        """
        Generate response from the model.
        
        Args:
            prompt: User input prompt
            system_prompt: System prompt for behavior
            conversation_history: Previous conversation turns
            **kwargs: Additional parameters to override defaults
            
        Returns:
            Dict containing response and metadata
        """
        start_time = time.time()
        
        # Build history for OpenAI call
        history = self._build_prompt(prompt, system_prompt, conversation_history)
        
        payload = {
            "message": prompt,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 512),
            "history": history
        }
        
        try:
            logger.debug(f"Sending request to model: {json.dumps(payload, indent=2)}")

            response = self.session.post(
                f"{self.endpoint}/chat",
                json=payload,
                timeout=TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            
            result = response.json()
            elapsed_ms = int((time.time() - start_time) * 1000)
            
            return {
                "response": result.get("response", ""),
                "model": result.get("model", self.model_name),
                "latency_ms": elapsed_ms,
                "deterministic": payload["temperature"] == 0,
            }
            
        except requests.exceptions.Timeout:
            logger.error(f"Model request timed out after {TIMEOUT_SECONDS}s")
            raise TimeoutError(f"Model generation timed out after {TIMEOUT_SECONDS}s")
        except requests.exceptions.RequestException as e:
            logger.error(f"Model request failed: {e}")
            raise RuntimeError(f"Failed to generate response: {e}")
    
    def _build_prompt(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None,
    ) -> list:
        """
        Build history for backend in [{"role": "...", "content": "..."}] format.
            
        Args:
            user_prompt: Current user input
            system_prompt: System instructions
            conversation_history: List of previous turns 
        """
        history = []

        # Add system prompt if provided
        if system_prompt:
            history.append({"role": "system", "content": system_prompt})
        
        # Add conversation history if provided
        if conversation_history:
            for turn in conversation_history:
                role = turn.get("role", "user")
                content = turn.get("content", "")
                history.append({"role": role, "content": content})
        history.append({"role": "user", "content": user_prompt})
        
        return history
    
    def health_check(self) -> bool:
        """
        Check if model provider is healthy.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            response = self.session.get(
                f"{self.endpoint}/api/tags",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False


# Singleton instance
_provider_instance = None


def get_provider() -> ModelProvider:
    """Get or create singleton model provider instance."""
    global _provider_instance
    if _provider_instance is None:
        _provider_instance = ModelProvider()
    return _provider_instance