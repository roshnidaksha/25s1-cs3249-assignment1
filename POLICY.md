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
CRISIS_KEYWORDS = [
    # Direct suicide mentions:
    "suicide", "end my life", "kill myself", "want to die", "can't go on", "take my life", "jump off",
    "end it all", 
    
    # Self-harm expressions:
    "hurt myself", "self-harm", "cut myself", "bleed myself", "injure myself",
    
    # Imminent danger indicators:
    "goodbye forever", "final message", "won't see you tomorrow", "no reason to live", "nothing matters anymore", "sleep forever", "sleep to end", "bye forever",
    
    # Emotional crisis expressions:
    "hopeless", "worthless", "useless", "overwhelmed", "lost hope"
]

CRISIS_PATTERNS = [
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
```

**Action**: `BLOCK` + Crisis referral

**Response Template**: 

```text
I'm deeply concerned about what you're sharing. Your safety is my top priority, and I want you to know that help is available.

You are not alone in this—there are people who care deeply about your wellbeing and want to support you. It takes courage to reach out and share your feelings, and that is an important first step toward healing. No matter how overwhelming things may feel, support and hope are always available, even in the darkest moments.

Please consider reaching out to trained crisis counselors immediately:
- National Suicide Prevention Lifeline: 988 (24/7)
- Crisis Text Line: Text HOME to 741741

If you feel comfortable, talk to someone you trust or a mental health professional as soon as possible. Your feelings are valid, and there are resources and people ready to help you through this difficult time. Remember, seeking help is a sign of strength, not weakness. You deserve compassion, understanding, and support. Please take care of yourself and allow others to help you—there is hope, and things can always get better.
```

#### 1.2 Medical Requests

**Definition**: Requests for diagnosis, treatment, or medication advice

**Implementation Requirements**:
- Define more medical keywords
- Create more regex patterns
- Use SAFE_FALLBACK action

```python
MEDICAL_INDICATORS = [
    # Diagnosis requests:
    "diagnose", "what condition", "illness", "disorder",
    
    # Medication/treatment:
    "medication", "what pills", "medicine", "tablet", "prescribe",
    "pain killer", "dosage", "drug",
    
    # Mental health specific:
    "am i depressed", "bipolar", "allergic", "syndrome", "phobia",
    "anxious", "anxiety", "depressed", "sad", "symptoms",
    "stress", "ocd", "insomnia", "adhd"
]

MEDICAL_PATTERNS = [
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
```

**Action**: `SAFE_FALLBACK`

**Response Template**: 

```text
I understand that you may be seeking medical advice or guidance, and I truly appreciate that you’ve chosen to reach out here. Your health and wellbeing are very important, but it’s important for me to be clear: 

I am not a medical professional, and I cannot provide medical diagnoses, prescribe medication, or recommend specific treatments. Matters such as diagnosis, dosage, or medication changes are best discussed directly with a licensed psychiatrist, psychologist, or healthcare provider who can evaluate your situation in detail and give you the care you deserve.

What I can offer is emotional support, a safe space to share what you are going through, and resources that may help you cope with feelings of stress, anxiety, or sadness. I can also guide you towards healthy coping strategies, mindfulness practices, or daily routines that may provide comfort. If you are struggling, please know that seeking professional help is a sign of strength, not weakness, and you don’t have to face this alone. You deserve care, support, and understanding.
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
```

**Action**: `BLOCK`

**Example Response Template**: 

```text
I need to be very clear: I cannot and will not provide assistance with harmful, violent, or illegal requests. Engaging in these types of conversations could potentially cause harm, and keeping our interaction safe and respectful is my top priority. This boundary isn’t meant to hurt you but to protect both you and others from unsafe or destructive outcomes.

While I cannot support harmful actions, what I can do is focus on healthier, positive, and constructive topics that may be helpful for you. If you’re experiencing strong feelings like anger, frustration, or hopelessness, I can provide a space to talk about those emotions safely. I can also share coping strategies for stress, guidance for building healthier habits, or encouragement as you work through personal challenges.

If your request comes from a place of emotional pain, it might help to know that talking to a counselor, therapist, or trusted professional could give you the support you deserve. You don’t have to go through difficult moments alone, there are always safer and more hopeful paths forward.
```

#### 1.4 Supportive Dialogue

**Definition**: General emotional support, stress discussion, life challenges

**Acceptable Topics**:
```python
SUPPORTIVE_TOPICS = [
    "stress management",
    "relationship challenges",
    "work-life balance",
    "anxiety coping",
    "grief and loss",
    "goal setting",
    "motivation",
    "self-esteem",
    "loneliness",
    "coping with change",
    "time management",
    "academic pressure",
    "family conflict",
    "building healthy habits",
    "mindfulness and relaxation",
    "dealing with failure",
    "confidence building"
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
    """
}
```
