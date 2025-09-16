"""
Model provider module for OpenAI (Responses API) integration.
"""

import json
import logging
import time
import os
from dotenv import load_dotenv
from typing import Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import TEMPERATURE, TOP_P, MAX_TOKENS, TIMEOUT_SECONDS

logger = logging.getLogger(__name__)
load_dotenv()  # Load .env if present

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-REPLACE_ME")

OPENAI_MODEL_CHAIN = [
    "gpt-4o-mini",
    "gpt-4.1-mini",
]

OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com")


class ModelProvider:
    """Handles communication with OpenAI Responses API (GPT-4 mini)."""

    def __init__(self):
        if not OPENAI_API_KEY or OPENAI_API_KEY.startswith("sk-REPLACE_ME"):
            raise RuntimeError("Please set OPENAI_API_KEY at the top of model_provider.py")
        self.endpoint = f"{OPENAI_BASE_URL}/v1/responses"
        self.session = self._create_session()
        self.model_name = self._pick_first_healthy_model(OPENAI_MODEL_CHAIN)

    # ---------- Session & health ----------
    def _create_session(self) -> requests.Session:
        s = requests.Session()
        retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry)
        s.mount("http://", adapter)
        s.mount("https://", adapter)
        s.headers.update({
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        })
        return s

    def _probe(self, model: str) -> bool:
        """Minimal health check using strict typed content; 1 token only."""
        payload = {
            "model": model,
            "instructions": "Health check.",
            "input": [
                {"role": "user", "content": [{"type": "input_text", "text": "ping"}]}
            ],
            "max_output_tokens": 16
        }
        try:
            r = self.session.post(self.endpoint, json=payload, timeout=5)
            ok = (r.status_code == 200)
            if not ok:
                logger.warning(f"Probe for {model} failed: {r.status_code} {r.text}")
            return ok
        except Exception as e:
            logger.warning(f"Probe for {model} raised: {e}")
            return False

    def _pick_first_healthy_model(self, chain: List[str]) -> str:
        for m in chain:
            if self._probe(m):
                logger.info(f"Using OpenAI model: {m}")
                return m
        raise RuntimeError("No usable GPT-4 mini model found. Try another model name in OPENAI_MODEL_CHAIN.")

    # ---------- Public API  ----------

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None,
        **kwargs
    ) -> Dict:
        """
        Generate a response using the OpenAI Responses API.

        Returns a dict with keys:
        - response (text), model (string), created_at, done, context (list),
          total_duration (ns), latency_ms (int), deterministic (bool)
        """
        start = time.time()

        # Config knobs with per-call overrides
        temperature = kwargs.get("temperature", TEMPERATURE)
        top_p = kwargs.get("top_p", TOP_P)
        max_out = kwargs.get("num_predict", MAX_TOKENS)
        max_out = max(16, int(max_out or 16))

        # Build a compact user message (system goes into 'instructions')
        history_text = ""
        if conversation_history:
            for turn in conversation_history:
                role = turn.get("role", "user")
                content = turn.get("content", "")
                if content:
                    history_text += f"\n[{role.upper()}]: {content}"

        user_text = (history_text + f"\n[USER]: {prompt}").strip()

        payload = {
            "model": self.model_name,
            "instructions": system_prompt or "",
            "input": [
                {"role": "user", "content": [{"type": "input_text", "text": user_text}]}
            ],
            "temperature": temperature,
            "top_p": top_p,
            "max_output_tokens": max_out
        }

        try:
            logger.debug(f"Sending request to OpenAI: {json.dumps(payload)[:800]}...")
            resp = self.session.post(self.endpoint, json=payload, timeout=TIMEOUT_SECONDS)
            if resp.status_code != 200:
                raise RuntimeError(f"OpenAI error {resp.status_code}: {resp.text}")

            data = resp.json()
            text = self._extract_text(data)
            elapsed_ms = int((time.time() - start) * 1000)

            return {
                "response": text,
                "model": data.get("model", self.model_name),
                "created_at": data.get("created_at", ""),
                "done": data.get("status", "completed") == "completed" or data.get("done", True),
                "context": [],  # Responses API does not expose token ctx like Ollama
                "total_duration": elapsed_ms * 1_000_000,  # ns, to mirror original shape
                "latency_ms": elapsed_ms,
                "deterministic": (temperature == 0),
            }

        except requests.exceptions.Timeout:
            logger.error(f"Model request timed out after {TIMEOUT_SECONDS}s")
            raise TimeoutError(f"Model generation timed out after {TIMEOUT_SECONDS}s")
        except Exception as e:
            logger.error(f"Model request failed: {e}")
            raise

    # ---------- Helpers ----------

    def _extract_text(self, result: Dict) -> str:
        """Prefer 'output_text'; else stitch any text parts from 'output'."""
        if isinstance(result.get("output_text"), str):
            return result["output_text"].strip()
        chunks = []
        for item in result.get("output", []):
            if item.get("type") == "message":
                for part in item.get("content", []):
                    if part.get("type") in ("output_text", "text"):
                        chunks.append(part.get("text", ""))
        return "".join(chunks).strip()

    def health_check(self) -> bool:
        return self._probe(self.model_name)


# Singleton instance (unchanged)
_provider_instance = None
def get_provider() -> ModelProvider:
    """Get or create singleton model provider instance."""
    global _provider_instance
    if _provider_instance is None:
        _provider_instance = ModelProvider()
    return _provider_instance