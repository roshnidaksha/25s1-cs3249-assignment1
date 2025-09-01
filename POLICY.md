# Safety and Moderation Policy

## Overview

This document defines the safety boundaries and moderation policies for the psychological pre-consultation CUI system. The system prioritizes user safety while providing supportive dialogue within appropriate boundaries.

## Policy Framework

### 1. Safety Categories

#### 1.1 Crisis Situations

**Definition**: Immediate risk of harm to self or others

**Implementation Requirements**: 
- Add more crisis keywords
- Create more regex patterns for complex expressions
- Use highest sensitivity in all safety modes

```python
# Student Implementation Required:
# Minimum 20 keywords covering various crisis expressions
CRISIS_KEYWORDS = [
    # Direct suicide mentions (examples - add more keywords):
    "suicide", "end my life",
    
    # Self-harm expressions (examples - add more keywords):
    "hurt myself", "self-harm",
    
    # Imminent danger indicators (examples - add more keywords):
    "goodbye forever", "final message",
    
    # TODO: Add more keywords to reach minimum 20
]

# Minimum 8 regex patterns for complex expressions
CRISIS_PATTERNS = [
    # Example patterns (add more regex patterns):
    r"\b(want|going|plan|ready) to (die|kill|hurt|end)\b",
    r"\b(thinking|thought) about (suicide|dying|ending it)\b",
    
    # TODO: Add more patterns to reach minimum 8
]
```

**Action**: `BLOCK` + Crisis referral

**Example Response Template (Complete this with 150-200 words)**: 

```text
I'm deeply concerned about what you're sharing. Your safety is my top priority, and I want you to know that help is available right now.

Please reach out to trained crisis counselors immediately:
- National Suicide Prevention Lifeline: 988 (24/7)
- Crisis Text Line: Text HOME to 741741

[TODO: Add 2-3 more sentences of supportive content]
[TODO: Add encouraging closing statement]
```

#### 1.2 Medical Requests

**Definition**: Requests for diagnosis, treatment, or medication advice

**Implementation Requirements**:
- Define more medical keywords
- Create more regex patterns
- Use SAFE_FALLBACK action

```python
# Student Implementation Required:
# Minimum 20 keywords
MEDICAL_INDICATORS = [
    # Diagnosis requests (add more keywords):
    "diagnose", "what condition",
    
    # Medication/treatment (add more keywords):
    "medication", "what pills",
    
    # Mental health specific (add more keywords):
    "am i depressed", "bipolar",
    
    # TODO: Add more keywords to reach minimum 20
]

# Minimum 8 regex patterns for complex expressions
MEDICAL_PATTERNS = [
    r"\b(prescribe|recommend|suggest) (medication|pills|drugs)\b",
    r"\bwhat (medication|medicine|pills) should i take\b",

    # TODO: Add more patterns to reach minimum 8
]
```

**Action**: `SAFE_FALLBACK`

**Response Template (Complete with structured format)**: 

```text
I understand you're looking for medical guidance, and I appreciate you reaching out. However, I'm not qualified to provide medical diagnoses or treatment recommendations.

[TODO: Add acknowledgment of specific concern if appropriate]

For your health and safety, please consult with:
- A licensed psychiatrist for medication questions

[TODO: Add 2-3 sentences about what you CAN offer]
```

#### 1.3 Harmful Content

**Definition**: Violence, illegal activities, harassment

**Implementation Requirements**:
- Minimum 20 keywords
- Consider both direct and indirect expressions

```python
# Student Implementation Required:
HARMFUL_CATEGORIES = {
    "violence": [
        "attack", "revenge",
        # TODO: Add more keywords
    ],
    
    "illegal": [
        "buy drugs", "sell drugs", 
        # TODO: Add more keywords
    ],
    
    "harassment": [
        "hate speech", "discriminate",
        # TODO: Add more keywords
    ]
}
```

**Action**: `BLOCK`

**Example Response Template (Complete this with 150-200 words)**: 

```text
I cannot and will not provide assistance with that request as it could potentially cause harm.

[TODO: Add clear boundary statement and redirect to appropriate topics]
```

#### 1.4 Supportive Dialogue

**Definition**: General emotional support, stress discussion, life challenges

**Acceptable Topics** (define at least 10):
```python
SUPPORTIVE_TOPICS = [
    "stress management",
    "relationship challenges",
    "work-life balance",
    "anxiety coping",
    "grief and loss",
    # TODO: Add at least 5 more acceptable topics
]
```

**Action**: `ALLOW`

### 2. Action Definitions

- **ALLOW**: Proceed with normal dialogue
- **BLOCK**: Refuse interaction with safety message and resources
- **SAFE_FALLBACK**: Redirect to appropriate resources while maintaining support

### 3. Confidence and Ambiguity

**Confidence Score Guidelines**:
- Keyword match: 0.7 confidence
- Pattern match: 0.8-0.9 confidence
- Multiple matches: Use maximum confidence

**Implementation Requirements**:
- Complete confidence thresholds by safety mode

**Confidence Thresholds by Safety Mode**:

```python
CONFIDENCE_THRESHOLDS = {
    "strict": {
        # Maximum sensitivity - err on side of caution
        "crisis": 0.3,   # Very low threshold for crisis detection
        "medical": 0.4,  # Low threshold for medical boundaries
        "harmful": 0.5   # Moderate threshold for harmful content
    },
    "balanced": {
        # Balanced approach for production use
        "crisis": , # TODO: Add confidence
        "medical": , # TODO: Add confidence 
        "harmful": , # TODO: Add confidence 
    },
    "permissive": {
        # Minimum filtering - only clear violations
        "crisis": , # TODO: Add confidence 
        "medical": , # TODO: Add confidence 
        "harmful": , # TODO: Add confidence
    }
}
```

### 5. Response Templates

**Implementation Requirements**:
- Copy the complete crisis template from your completed 1.1 Crisis Situations above.
- Copy the complete medical template from your completed 1.2 Medical Requests above.
- Copy the complete harmful template from your completed 1.3 Harmful Content above.
- Complete disclaimer template.

```python
RESPONSE_TEMPLATES = {
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
    """
}
```
