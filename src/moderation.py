"""
Content moderation module for safety enforcement.
Students must complete TODO sections according to POLICY.md.
"""

import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

from .config import SAFETY_MODE

logger = logging.getLogger(__name__)


class ModerationAction(Enum):
    """Possible moderation actions."""
    ALLOW = "allow"
    BLOCK = "block"
    SAFE_FALLBACK = "safe_fallback"


@dataclass
class ModerationResult:
    """Result of moderation check."""
    action: ModerationAction
    tags: List[str]  # Policy tags that were triggered
    reason: str  # Human-readable explanation
    confidence: float  # Confidence level (0-1)
    fallback_response: Optional[str] = None  # Response to use if action != ALLOW


class Moderator:
    """Handles content moderation according to safety policy."""
    
    def __init__(self):
        """Initialize the moderator with safety rules."""
        self.safety_mode = SAFETY_MODE
        self._initialize_rules()
    
    def _initialize_rules(self):
        """
        Initialize moderation rules based on POLICY.md.
        TODO: Students must define these based on their POLICY.md
        
        IMPLEMENTATION GUIDE:
        1. Copy all keywords and patterns from your completed POLICY.md
        2. Ensure Python formatting (lists, strings, regex compilation)
        3. Templates should be multi-line strings with proper formatting
        """
        
        # TODO: Define crisis keywords and patterns
        # These should detect immediate risk of harm
        self.crisis_keywords = [
            # Example (students should expand):
            # "suicide", "end my life"
            # TODO: Add comprehensive list
        ]
        
        # TODO: Crisis patterns - regex for complex expressions
        self.crisis_patterns = [
            # Example regex patterns:
            # r"\b(want|going|plan|ready) to (die|kill|hurt|end)\b",
            # TODO: Add patterns for crisis detection
        ]
        
        # TODO: Define medical request patterns
        self.medical_keywords = [
            # Examples:
            # "diagnose", "what condition",
            # TODO: Add medical request indicators
        ]
        
        # TODO: Medical patterns - regex for complex expressions
        self.medical_patterns = [
            # Example regex patterns:
            # r"\b(prescribe|recommend|suggest) (medication|pills|drugs)\b",
            # TODO: Add patterns for medical detection
        ]
        
        # TODO: Define harmful content patterns
        self.harmful_content = {
            "violence": [],  # TODO: Violence indicators
            "illegal": [],   # TODO: Illegal activity indicators
            "harassment": [] # TODO: Harassment indicators
        }
        
        # TODO: Define confidence thresholds based on safety mode
        self.confidence_thresholds = {
            "strict": { 
                "crisis": 0.3,
                "medical": 0.4,
                "harmful": 0.5,
            },
            "balanced": { 
                # TODO: Adjust these
                "crisis": 0.5,
                "medical": 0.5,
                "harmful": 0.5,
            },
            "permissive": { 
                # TODO: Adjust these
                "crisis": 0.5,
                "medical": 0.5,
                "harmful": 0.5,
            }
        }
        
        # TODO: Define safety fallback templates
        # Copy complete templates from POLICY.md
        self.fallback_templates = {
            "crisis": """
I'm deeply concerned about what you're sharing. Your safety is my top priority, and I want you to know that help is available right now.

Please reach out to trained crisis counselors immediately:
- National Suicide Prevention Lifeline: 988 (24/7)
- Crisis Text Line: Text HOME to 741741

[TODO: Add 2-3 more sentences of supportive content]
[TODO: Add encouraging closing statement]
            """,
            
            "medical": """
I understand you're looking for medical guidance, and I appreciate you reaching out. However, I'm not qualified to provide medical diagnoses or treatment recommendations.

[TODO: Add acknowledgment of specific concern if appropriate]

For your health and safety, please consult with:
- A licensed psychiatrist for medication questions

[TODO: Add 2-3 sentences about what you CAN offer]
            """,

            "harmful": """
I cannot and will not provide assistance with that request as it could potentially cause harm.

[TODO: Add clear boundary statement and redirect to appropriate topics]
            """,
            
            "disclaimer": """
Welcome to the Psychological Pre-Consultation Support System.

IMPORTANT DISCLAIMER:
This is an AI support system designed to provide initial emotional support and guidance. Please note:
[TODO: Add 4-5 bullet points about system limitations]

When to Seek Immediate Help:
[TODO: Add crisis indicators and resources]

What I Can Offer:
[TODO: Add 4-5 bullet points about available support]

Your wellbeing is important. How can I support you today?
            """,
        }
    
    def moderate(
        self,
        user_prompt: str,
        model_response: Optional[str] = None,
        context: Optional[List[Dict]] = None,
    ) -> ModerationResult:
        """
        Perform moderation on user input and/or model output.
        
        Args:
            user_prompt: The user's input text
            
        Returns:
            ModerationResult with action and explanation
            
        IMPLEMENTATION ORDER:
        1. Check crisis (highest priority - must not miss)
        2. Check medical (prevent harmful advice)
        3. Check harmful content (filter inappropriate)
        """
        
        # Example skeleton:
        # Step 1: Check for crisis indicators (highest priority)
        crisis_check = self._check_crisis(user_prompt)
        if crisis_check.action != ModerationAction.ALLOW:
            logger.warning(f"Crisis detected: {crisis_check.reason}")
            return crisis_check
        
        # TODO: Other Steps - Check for ???

        # If model response provided, check it
        if model_response:
            output_check = self._check_model_output(model_response)
            if output_check.action != ModerationAction.ALLOW:
                logger.warning(f"Output violation: {output_check.reason}")
                return output_check
        
        # Check context for concerning patterns
        if context:
            context_check = self._check_context_patterns(context)
            if context_check.action != ModerationAction.ALLOW:
                logger.info(f"Context concern: {context_check.reason}")
                return context_check
        
        # Default: Allow
        return ModerationResult(
            action=ModerationAction.ALLOW,
            tags=[],
            reason="Content passes all safety checks",
            confidence=1.0,
        )
    
    def _check_crisis(self, text: str) -> ModerationResult:
        """
        Check for crisis indicators.
        
        TODO: Implement crisis detection
        
        ALGORITHM:
        1. Convert text to lowercase
        2. Check against crisis_keywords:
           - If found, set confidence = 0.7
           - Track which keywords were found
        3. Check against crisis_patterns:
           - If matched, set confidence = 0.8-0.9
           - Use re.search() for each pattern
        4. If multiple matches, use MAXIMUM confidence
        5. Get threshold for current safety_mode
        6. If confidence >= threshold:
           - Return BLOCK action
           - Include crisis fallback_response
           - Add descriptive tags
        7. Otherwise return ALLOW
        """

        text_lower = text.lower()
        detected_keywords = []
        confidence = 0.0
        
        return ModerationResult(
            action=ModerationAction.ALLOW,
            tags=[],
            reason="No crisis indicators detected",
            confidence=confidence,
        )
    
    def _check_medical(self, text: str) -> ModerationResult:
        """
        Check for medical requests.
        
        TODO: Implement medical request detection
        
        ALGORITHM:
        1. Convert text to lowercase
        2. Check against medical_keywords (confidence = 0.7)
        3. Check against medical_patterns (confidence = 0.85)
        4. Use maximum confidence if multiple matches
        5. Compare against threshold for safety_mode
        6. Return SAFE_FALLBACK if threshold exceeded
        
        Note: Use SAFE_FALLBACK, not BLOCK, for medical requests
        """
        text_lower = text.lower()
        detected_keywords = []
        confidence = 0.0

        # TODO: Implement keyword checking
        # Similar to crisis checking but with medical keywords
        
        # TODO: Implement pattern checking
        # Similar to crisis checking but with medical patterns
        
        # TODO: Threshold comparison and return
        # Remember to use ModerationAction.SAFE_FALLBACK for medical
        
        return ModerationResult(
            action=ModerationAction.ALLOW,
            tags=[],
            reason="No medical requests detected",
            confidence=confidence,
        )
    
    def _check_harmful(self, text: str) -> ModerationResult:
        """
        Check for harmful content.
        
        TODO: Implement harmful content detection
        
        ALGORITHM:
        1. Convert text to lowercase
        2. For each category in harmful_content:
           - Check if any keywords present
           - Track which categories triggered
        3. Set confidence = 0.75 for any match
        4. Compare against threshold
        5. Return BLOCK if threshold exceeded
        
        Include triggered categories in tags for debugging
        """

        text_lower = text.lower()
        detected_categories = []
        confidence = 0.0
        
        return ModerationResult(
            action=ModerationAction.ALLOW,
            tags=[],
            reason="No harmful content detected",
            confidence=confidence,
        )
    
    def _check_model_output(self, response: str) -> ModerationResult:
        """
        Check model output for policy violations.
        
        TODO: Ensure model didn't provide medical advice or break boundaries
        
        ALGORITHM:
        1. Check for medical_keywords that shouldn't appear
        2. Look for diagnosis-like statements
        3. Check for treatment recommendations
        4. Return SAFE_FALLBACK if violations found

        """

        response_lower = response.lower()
        
        return ModerationResult(
            action=ModerationAction.ALLOW,
            tags=[],
            reason="Model output is appropriate",
            confidence=1.0,
        )
    
    def _check_context_patterns(self, context: List[Dict]) -> ModerationResult:
        
        # Check for escalation
        crisis_count = 0
        for turn in context:
            if turn.get("role") == "user":
                content = turn.get("content", "").lower()
                for keyword in self.crisis_keywords:
                    if keyword in content:
                        crisis_count += 1
        
        if crisis_count >= 3:
            return ModerationResult(
                action=ModerationAction.SAFE_FALLBACK,
                tags=["pattern_escalation", "repeated_crisis"],
                reason="Escalating crisis pattern detected",
                confidence=0.8,
                fallback_response=self.fallback_templates["crisis"],
            )
        
        return ModerationResult(
            action=ModerationAction.ALLOW,
            tags=[],
            reason="Conversation pattern is safe",
            confidence=1.0,
        )
    
    def get_disclaimer(self) -> str:
        """Get initial disclaimer."""
        return self.fallback_templates.get("disclaimer", "")

# Singleton instance
_moderator_instance = None

def get_moderator() -> Moderator:
    """Get singleton moderator instance."""
    global _moderator_instance
    if _moderator_instance is None:
        _moderator_instance = Moderator()
    return _moderator_instance