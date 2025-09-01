"""
Model provider module for Ollama integration.
This module is complete - students should NOT modify.
"""

import json
import logging
import time
from typing import Dict, List, Optional, Union

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import (
    MODEL_ENDPOINT,
    MODEL_NAME,
    TIMEOUT_SECONDS,
    get_model_config,
)

logger = logging.getLogger(__name__)


class ModelProvider:
    """Handles communication with Ollama API."""
    
    def __init__(self):
        """Initialize the model provider with retry logic."""
        self.endpoint = MODEL_ENDPOINT
        self.model_name = MODEL_NAME
        self.session = self._create_session()
        self._verify_connection()
    
    def _create_session(self) -> requests.Session:
        """Create HTTP session with retry logic."""
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
        """Verify Ollama is running and model is available."""
        try:
            # Check Ollama is running
            response = self.session.get(
                f"{self.endpoint}/api/tags",
                timeout=5
            )
            response.raise_for_status()
            
            # Check model is available
            models = response.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            
            if self.model_name not in model_names:
                available = ", ".join(model_names) if model_names else "none"
                raise RuntimeError(
                    f"Model '{self.model_name}' not found. "
                    f"Available models: {available}. "
                    f"Run: ollama pull {self.model_name}"
                )
            
            logger.info(f"Successfully connected to Ollama with model {self.model_name}")
            
        except requests.exceptions.ConnectionError:
            raise RuntimeError(
                "Cannot connect to Ollama. Please ensure:\n"
                "1. Ollama is installed\n"
                "2. Ollama service is running (run: ollama serve)\n"
                "3. Port 11434 is not blocked"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to verify Ollama connection: {e}")
    
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
        
        # Prepare the full prompt
        full_prompt = self._build_prompt(prompt, system_prompt, conversation_history)
        
        # Get model configuration
        config = get_model_config()
        
        # Override with any provided kwargs
        if kwargs:
            config["options"].update(kwargs)
        
        # Prepare request
        request_data = {
            "model": config["model"],
            "prompt": full_prompt,
            "stream": False,
            "options": config["options"],
        }
        
        try:
            logger.debug(f"Sending request to model: {json.dumps(request_data, indent=2)}")
            
            response = self.session.post(
                f"{self.endpoint}/api/generate",
                json=request_data,
                timeout=TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            
            result = response.json()
            elapsed_ms = int((time.time() - start_time) * 1000)
            
            return {
                "response": result.get("response", ""),
                "model": result.get("model", self.model_name),
                "created_at": result.get("created_at", ""),
                "done": result.get("done", True),
                "context": result.get("context", []),
                "total_duration": result.get("total_duration", 0),
                "latency_ms": elapsed_ms,
                "deterministic": config["options"]["temperature"] == 0,
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
    ) -> str:
        """
        Build full prompt with system prompt and conversation history.
        
        Args:
            user_prompt: Current user input
            system_prompt: System instructions
            conversation_history: List of previous turns
            
        Returns:
            Formatted prompt string
        """
        parts = []
        
        # Add system prompt if provided
        if system_prompt:
            parts.append(f"### System Instructions ###")
            parts.append(system_prompt)
            parts.append("\n### Conversation ###\n")
        
        # Add conversation history if provided
        if conversation_history:
            for turn in conversation_history:
                role = turn.get("role", "user")
                content = turn.get("content", "")
                if role == "user":
                    parts.append(f"User: {content}")
                elif role == "assistant":
                    parts.append(f"Assistant: {content}")
            parts.append("")  # Empty line before current prompt
        
        # Add current user prompt
        parts.append(f"User: {user_prompt}")
        parts.append("\n### Response ###")
        parts.append("Assistant: ")
        
        return "\n".join(parts)
    
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