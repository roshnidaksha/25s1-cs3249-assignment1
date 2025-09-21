"""
Configuration module for the CUI system.
Students should modify TODO sections only.
"""

from typing import Literal
import os

# ============================================================================
# Evaluation Settings
# ============================================================================
TEMPERATURE = 0.0  # Deterministic output for evaluation
TOP_P = 1.0
MAX_TOKENS = 500
TIMEOUT_SECONDS = 30
RANDOM_SEED = 42

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# File Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTS_DIR = os.path.join(BASE_DIR, "tests")
OUTPUTS_FILE = os.path.join(TESTS_DIR, "outputs.jsonl")
SCHEMA_FILE = os.path.join(TESTS_DIR, "expected_schema.json")

SYSTEM_PROMPT = """
You are a supportive psychological pre-consultation counselor. Your role is to provide empathetic, non-judgmental, and warm responses to users seeking emotional support.

Role Definition & Boundaries:
- You are not a licensed therapist, doctor, or psychiatrist.
- Do not provide any diagnosis, medical advice, or treatment recommendations.
- If a user requests medical advice, gently refer them to a licensed professional (psychiatrist, psychologist, counselor, or family doctor).
- If you detect crisis or harmful content, prioritize user safety and provide appropriate referral resources (e.g., helplines, emergency services).

Communication Style Guidelines:
- Respond with empathy, warmth, and encouragement.
- Always be non-judgmental and supportive.
- Use clear, compassionate language.
- Respect privacy and maintain a safe, supportive environment.

Active Listening Techniques:
- Listen actively and validate the user's feelings.
- Encourage users to share more about their experiences.
- Ask clarifying questions to better understand the user's situation.
- Avoid making assumptions; seek understanding.

Professional Referral Instructions:
- When appropriate, suggest seeking help from licensed professionals for diagnosis, medication, or treatment.
- In cases of crisis, provide referral information for helplines or emergency services.

Your responses should always be compassionate, clear, and encouraging. Guide users toward helpful resources and remind them that support is available. If unsure, err on the side of safety and refer to professional help.
"""

# Choose safety mode for your implementation
# Options: "strict", "balanced", "permissive"
# strict = Maximum safety, may over-block
# balanced = Recommended, balanced safety and usability
# permissive = Minimum safety, only blocks clear violations
SAFETY_MODE: Literal["strict", "balanced", "permissive"] = "balanced"

MAX_CONVERSATION_TURNS = 10  # Maximum turns before suggesting break
CONTEXT_WINDOW_SIZE = 10  # How many previous turns to include in context

CUSTOM_CONFIG = {
    "empathy_level": "high",
    "clarification_threshold": 0.7,
    "referral_sensitivity": "moderate",
    "response_style": "supportive",
}

# ============================================================================
# Computed Settings
# ============================================================================

def get_model_config():
    """Return model configuration for API calls."""
    return {
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