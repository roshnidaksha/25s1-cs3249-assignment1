"""
Content moderation module for safety enforcement.
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
        Initialize moderation rules based on POLICY.md
        """

        # These should detect immediate risk of harm
        self.crisis_keywords = [
            # Direct suicide mentions:
            "suicide", "end my life", "kill myself", "want to die", "can't go on", "take my life", "jump off",
            "end it all", 
            
            # Self-harm expressions:
            "hurt myself", "self-harm", "cut myself", "bleed myself", "injure myself",
            
            # Imminent danger indicators:
            "goodbye forever", "final message", "won't see you tomorrow", "no reason to live", "nothing matters anymore", "sleep forever", 
            "sleep to end", "bye forever",
            
            # Emotional crisis expressions:
            "hopeless", "worthless", "useless", "overwhelmed", "lost hope"
        ]

        self.crisis_patterns = [
            r"\b(want|wish|going|plan|ready) to (die|kill|hurt|end)\b",
            r"\b(thinking|thought) about (suicide|dying|ending it)\b",
            r"\b(no reason|nothing left) to live\b",
            r"\b(cut|hurt|injure|bleed|hang|stab) (myself|her|him|them)\b",
            r"\bi am going to (die|cut myself|end my life|kill myself|jump off)\b",
            r"\bi (don't|do not) want to (live|be here|exist)\b",
            r"\bi am (going|planning) to (take|consume|eat) poison\b",
            r"\bi (gobbled|ate|drank) (poison|pills)\b",
            r"\blife is .* painful\b"
        ]
        
        self.medical_keywords = [
            # Diagnosis requests:
            "diagnose", "what condition", "illness", "disorder", "disease", "syndrome",
            
            # Medication/treatment:
            "medication", "what pills", "medicine", "tablet", "prescribe",
            "pain killer", "dosage", "drug", "pill", "prescription", "treatment", 
            "therapy", "sedative",
            
            # Mental health specific:
            "am i depressed", "bipolar", "allergic", "syndrome", "phobia",
            "symptoms", "ocd", "insomnia", "adhd"
        ]
        
        self.medical_patterns = [
            r"\b(prescribe|recommend|suggest) (medication|pills|drugs)\b",
            r"\bwhat (medication|medicine|pills) (should i|to) take\b",
            r"\b(side effect[s]?|adverse effect[s]?) of (this|that|the) (medicine|drug|pill)\b",
            r"\b(am i|could i be|might i be) (depressed|bipolar|anxious|anxiety|ocd|adhd|insomnic)\b",
            r"\b(do i|could i|might i) have (depressed|bipolar|anxious|anxiety|ocd|adhd|insomnic)\b",
            r"\b(can you|could you|please) (diagnose|tell me what's wrong|say what's wrong) .* me\b",
            r"\b(how much|what dosage|how many) (pills|tablets|mg) .* take\b",
            r"\b(should i|can i) (stop|start|continue|change) (my )?(medication|pills|treatment)\b",
            r"\b(will|does|can) (this|that) (pill|medicine|drug) (help|work)\b"
            r"\b(symptom[s]? of|sign[s]? of) (this|that|the)\b",
        ]
        
        self.harmful_content = {
            "violence": [
                "attack", "revenge", "kill", "bomb", "shoot", "massacre", "stab", 
                "terrorist", "destroy", "assault", "murder", "explode", "gun"
            ],
            
            "illegal": [
                "buy drugs", "sell drugs", "smuggle", "hack", "steal", "scam", "fraud", 
                "blackmail", "illegal", "dark web", "launder money", "money launder"
            ],
            
            "harassment": [
                "hate speech", "discriminate", "bully", "harass", "stalk", "abuse", "threaten"
            ]
        }
        
        self.confidence_thresholds = {
            "strict": {
                # Maximum sensitivity - err on side of caution
                "crisis": 0.3,   # Very low threshold for crisis detection
                "medical": 0.4,  # Low threshold for medical boundaries
                "harmful": 0.5   # Moderate threshold for harmful content
            },
            "balanced": {
                # Balanced approach for production use
                "crisis": 0.6,   # Trigger only if reasonably sure
                "medical": 0.7, # Slightly higher than crisis
                "harmful": 0.7   # Needs strong signals to trigger
            },
            "permissive": {
                # Minimum filtering - only clear violations
                "crisis": 0.8,   # Only act on very clear crisis signals
                "medical": 0.85, # Only clear medical requests are blocked
                "harmful": 0.9   # Only definite harmful content is blocked
            }
        }
        

        self.fallback_templates = {
            "crisis": """
I'm deeply concerned about what you're sharing. Your safety is my top priority, and I want you to know that help is available.

You are not alone in this—there are people who care deeply about your wellbeing and want to support you. It takes courage to reach out and share your feelings, and that is an important first step toward healing. No matter how overwhelming things may feel, support and hope are always available, even in the darkest moments.

Please consider reaching out to trained crisis counselors immediately:
- National Suicide Prevention Lifeline: 988 (24/7)
- Crisis Text Line: Text HOME to 741741

If you feel comfortable, talk to someone you trust or a mental health professional as soon as possible. Your feelings are valid, and there are resources and people ready to help you through this difficult time. Remember, seeking help is a sign of strength, not weakness. You deserve compassion, understanding, and support. Please take care of yourself and allow others to help you—there is hope, and things can always get better.
    """,
    
    "medical": """
I understand that you may be seeking medical advice or guidance, and I truly appreciate that you’ve chosen to reach out here. Your health and wellbeing are very important, but it’s important for me to be clear: 

I am not a medical professional, and I cannot provide medical diagnoses, prescribe medication, or recommend specific treatments. Matters such as diagnosis, dosage, or medication changes are best discussed directly with a licensed psychiatrist, psychologist, or healthcare provider who can evaluate your situation in detail and give you the care you deserve.

What I can offer is emotional support, a safe space to share what you are going through, and resources that may help you cope with feelings of stress, anxiety, or sadness. I can also guide you towards healthy coping strategies, mindfulness practices, or daily routines that may provide comfort. If you are struggling, please know that seeking professional help is a sign of strength, not weakness, and you don’t have to face this alone. You deserve care, support, and understanding.
    """,

     "harmful": """
I need to be very clear: I cannot and will not provide assistance with harmful, violent, or illegal requests. Engaging in these types of conversations could potentially cause harm, and keeping our interaction safe and respectful is my top priority. This boundary isn’t meant to hurt you but to protect both you and others from unsafe or destructive outcomes.

While I cannot support harmful actions, what I can do is focus on healthier, positive, and constructive topics that may be helpful for you. If you’re experiencing strong feelings like anger, frustration, or hopelessness, I can provide a space to talk about those emotions safely. I can also share coping strategies for stress, guidance for building healthier habits, or encouragement as you work through personal challenges.

If your request comes from a place of emotional pain, it might help to know that talking to a counselor, therapist, or trusted professional could give you the support you deserve. You don’t have to go through difficult moments alone, there are always safer and more hopeful paths forward.
    """,
    
    "disclaimer": """
Welcome to the Psychological Pre-Consultation Support System.

IMPORTANT DISCLAIMER:
This is an AI support system designed to provide initial emotional support and guidance. Please note that:
* I am not a licensed therapist, doctor, or psychiatrist.
* I cannot provide medical diagnoses, prescriptions, or professional treatment plans.
* Conversations are for general emotional support only, not a substitute for professional care.
* Information shared here may be limited in accuracy compared to a trained clinician.
* If you are in immediate danger, this system is not a replacement for emergency services.

When to Seek Immediate Help:

If you are experiencing any of the following, please seek help right away:
* Thoughts of suicide, self-harm, or wanting to end your life.
* Feeling unsafe due to violence, abuse, or harassment.
* Severe emotional distress that feels unbearable or uncontrollable.

What I Can Offer:
* A listening space to share what’s on your mind.
* Emotional support for stress, anxiety, and life challenges.
* Coping strategies for daily struggles like motivation, confidence, or balance.
* Practical guidance on wellbeing topics (mindfulness, healthy habits, resilience).
* Encouragement to seek professional support when appropriate.

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
        
        # Step 1: Check for crisis indicators (highest priority)
        crisis_check = self._check_crisis(user_prompt)
        if crisis_check.action != ModerationAction.ALLOW:
            logger.warning(f"Crisis detected: {crisis_check.reason}")
            logger.warning(f"Action taken: {crisis_check.action}, Tags: {crisis_check.tags}")
            return crisis_check
        
        # Step 2: Check for medical requests
        medical_check = self._check_medical(user_prompt)
        if medical_check.action != ModerationAction.ALLOW:
            logger.warning(f"Medical request detected: {medical_check.reason}")
            logger.warning(f"Action taken: {medical_check.action}, Tags: {medical_check.tags}")
            return medical_check
        
        # Step 3: Check for harmful content
        harmful_check = self._check_harmful(user_prompt)
        if harmful_check.action != ModerationAction.ALLOW:
            logger.warning(f"Harmful content detected: {harmful_check.reason}")
            logger.warning(f"Action taken: {harmful_check.action}, Tags: {harmful_check.tags}")
            return harmful_check

        # If model response provided, check it
        if model_response:
            output_check = self._check_model_output(model_response)
            if output_check.action != ModerationAction.ALLOW:
                logger.warning(f"Output violation: {output_check.reason}")
                logger.warning(f"Action taken: {output_check.action}, Tags: {output_check.tags}")
                return output_check
        
        # Check context for concerning patterns
        if context:
            context_check = self._check_context_patterns(context)
            if context_check.action != ModerationAction.ALLOW:
                logger.info(f"Context concern: {context_check.reason}")
                logger.info(f"Action taken: {context_check.action}, Tags: {context_check.tags}")
                return context_check
        
        # Default: Allow
        logger.info("No issues detected")
        return ModerationResult(
            action=ModerationAction.ALLOW,
            tags=[],
            reason="Content passes all safety checks",
            confidence=1.0,
        )
    
    def _check_crisis(self, text: str) -> ModerationResult:
        """
        Check for crisis indicators.
        
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

        confidence = 0.0
        text_lower = text.lower()
        detected_keywords = [kw for kw in self.crisis_keywords if kw in text_lower]
        if len(detected_keywords) > 0:
            confidence = 0.7
            
        detected_patterns = [p for p in self.crisis_patterns if re.search(p, text_lower)]
        if detected_patterns:
            confidence = 0.85
            
        if detected_keywords and detected_patterns:
            confidence = max(confidence, 0.9)
            
        threshold = self.confidence_thresholds[self.safety_mode]["crisis"]
        if confidence >= threshold:
            return ModerationResult(
                action=ModerationAction.BLOCK,
                tags=detected_keywords,
                reason="Crisis indicators detected",
                confidence=confidence,
                fallback_response=self.fallback_templates["crisis"],
            )
        
        return ModerationResult(
            action=ModerationAction.ALLOW,
            tags=[],
            reason="No crisis indicators detected",
            confidence=confidence,
        )
    
    def _check_medical(self, text: str) -> ModerationResult:
        """
        Check for medical requests.
        
        ALGORITHM:
        1. Convert text to lowercase
        2. Check against medical_keywords (confidence = 0.7)
        3. Check against medical_patterns (confidence = 0.85)
        4. Use maximum confidence if multiple matches
        5. Compare against threshold for safety_mode
        6. Return SAFE_FALLBACK if threshold exceeded
        
        Note: Use SAFE_FALLBACK, not BLOCK, for medical requests
        """
        
        confidence = 0.0
        text_lower = text.lower()
        detected_keywords = [kw for kw in self.medical_keywords if kw in text_lower]
        if detected_keywords:
            confidence = 0.7
            
        detected_patterns = [p for p in self.medical_patterns if re.search(p, text_lower)]
        if detected_patterns:
            confidence = 0.85
        
        if detected_keywords and detected_patterns:
            confidence = max(confidence, 0.9)
        
        threshold = self.confidence_thresholds[self.safety_mode]["medical"]
        if confidence >= threshold:
            return ModerationResult(
                action=ModerationAction.SAFE_FALLBACK,
                tags=detected_keywords,
                reason="Medical request detected",
                confidence=confidence,
                fallback_response=self.fallback_templates["medical"],
            )
        
        return ModerationResult(
            action=ModerationAction.ALLOW,
            tags=[],
            reason="No medical requests detected",
            confidence=confidence,
        )
    
    def _check_harmful(self, text: str) -> ModerationResult:
        """
        Check for harmful content.
        
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

        confidence = 0.0
        text_lower = text.lower()
        detected_categories = []
        for cat in self.harmful_content:
            for kw in self.harmful_content[cat]:
                if kw in text_lower:
                    detected_categories.append(cat)
                    confidence = 0.75
                    break
                
        threshold = self.confidence_thresholds[self.safety_mode]["harmful"]
        if confidence >= threshold:
            return ModerationResult(
                action=ModerationAction.BLOCK,
                tags=detected_categories,
                reason="Harmful content detected",
                confidence=confidence,
                fallback_response=self.fallback_templates["harmful"],
            )
        
        return ModerationResult(
            action=ModerationAction.ALLOW,
            tags=[],
            reason="No harmful content detected",
            confidence=confidence,
        )
    
    def _check_model_output(self, response: str) -> ModerationResult:
        """
        Check model output for policy violations.
        
        ALGORITHM:
        1. Check for medical_keywords that shouldn't appear
        2. Look for diagnosis-like statements
        3. Check for treatment recommendations
        4. Return SAFE_FALLBACK if violations found

        """

        confidence = 0.0
        response_lower = response.lower()
        detected_keywords = [kw for kw in self.medical_keywords if kw in response_lower]
        if detected_keywords:
            confidence = 0.8
        
        detected_patterns = [p for p in self.medical_patterns if re.search(p, response_lower)]
        if detected_patterns:
            confidence = 0.85
            
        if detected_keywords and detected_patterns:
            confidence = max(confidence, 0.9)
        
        threshold = self.confidence_thresholds[self.safety_mode]["medical"]
        if confidence >= threshold:
            return ModerationResult(
                action=ModerationAction.SAFE_FALLBACK,
                tags=detected_keywords,
                reason="Model output violates medical policy",
                confidence=confidence,
                fallback_response=self.fallback_templates["medical"],
            )
        
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