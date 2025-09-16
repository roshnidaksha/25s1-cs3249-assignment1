"""
Configuration module for the CUI system.
Students should modify TODO sections only.
"""

from typing import Literal
from dotenv import load_dotenv
import os

load_dotenv()  # Load .env if present

# ============================================================================
# Evaluation Settings
# ============================================================================
TEMPERATURE = 0.0  # Deterministic output for evaluation
TOP_P = 1.0
MAX_TOKENS = 500
TIMEOUT_SECONDS = 30
RANDOM_SEED = 42

# Model Configuration

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is missing. Put it in your environment or a .env file.")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_PORT = int(os.getenv("OPENAI_PORT", 8001))
OPENAI_MODEL_ENDPOINT = f"http://localhost:{OPENAI_PORT}"
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# File Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTS_DIR = os.path.join(BASE_DIR, "tests")
OUTPUTS_FILE = os.path.join(TESTS_DIR, "outputs.jsonl")
SCHEMA_FILE = os.path.join(TESTS_DIR, "expected_schema.json")

SYSTEM_PROMPT = """
You are a supportive psychological pre-consultation counselor. Your role is to provide empathetic, non-judgmental, and warm responses to users seeking emotional support. You do not diagnose conditions, prescribe treatments, or offer medical advice. Instead, you listen actively, validate feelings, and encourage users to share more about their experiences.

Always maintain clear boundaries:

Do not provide any diagnosis or treatment recommendations.
If a user requests medical advice, gently refer them to a licensed professional.
If you detect crisis or harmful content, prioritize user safety and provide appropriate referral resources.
Your responses should be compassionate, clear, and encouraging. Ask clarifying questions when needed to better understand the user's situation. Guide users toward helpful resources and remind them that support is available. Always respect privacy and maintain a safe, supportive environment.
"""

# Choose safety mode for your implementation
# Options: "strict", "balanced", "permissive"
# strict = Maximum safety, may over-block
# balanced = Recommended, balanced safety and usability
# permissive = Minimum safety, only blocks clear violations
SAFETY_MODE: Literal["strict", "balanced", "permissive"] = "balanced"

MAX_CONVERSATION_TURNS = 10  # Maximum turns before suggesting break
CONTEXT_WINDOW_SIZE = 5  # How many previous turns to include in context

CUSTOM_CONFIG = {
    "empathy_level": "high",
    "clarification_threshold": 0.7,
    "referral_sensitivity": "moderate",
    "response_style": "supportive",
}

# ============================================================================
# Computed Settings (DO NOT MODIFY)
# ============================================================================

def get_model_config():
    """Return model configuration for API calls."""
    return {
        "model": MODEL_NAME,
        "options": {
            "temperature": TEMPERATURE,
            "top_p": TOP_P,
            "num_predict": MAX_TOKENS,
            "seed": RANDOM_SEED,
        }
    }

def validate_config():
    """Validate configuration on module import."""
    assert SAFETY_MODE in ["strict", "balanced", "permissive"], \
        f"Invalid SAFETY_MODE: {SAFETY_MODE}"
    assert 0 <= TEMPERATURE <= 1, f"Invalid TEMPERATURE: {TEMPERATURE}"
    assert 1 <= MAX_CONVERSATION_TURNS <= 50, \
        f"Invalid MAX_CONVERSATION_TURNS: {MAX_CONVERSATION_TURNS}"
    
# Run validation on import
validate_config()