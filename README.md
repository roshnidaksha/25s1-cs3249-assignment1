# Assignment 1: Building a Local LLM Psychological Pre-consultation Chatbot

## Project Overview


Mental health support systems play a critical role in providing accessible initial assistance to individuals seeking psychological help. This project implements a local LLM-based psychological pre-consultation chatbot designed to:

- Provide empathetic, non-judgmental, and supportive responses to users seeking emotional support
- Actively listen and validate user feelings
- Assess user needs and guide appropriate next steps
- Refer users to professional resources when necessary
- Maintain strict boundaries: the chatbot does NOT diagnose, prescribe, or offer medical advice or treatment

The chatbot uses OpenAI language models to simulate a safe, supportive conversation environment. It is intended for initial support only and is not a substitute for professional care. If a user is in crisis or needs urgent help, the system will provide referral information for emergency services and mental health professionals.

**Important**: This system is for educational purposes only and does NOT provide diagnoses or treatment recommendations.

## Repository Structure

```text
25s1-cs3249-assignment1/
├── README.md
├── Assignment 1.pdf
├── POLICY.md
├── INSTALL.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── model_provider.py
│   ├── moderation.py
│   ├── chat_engine.py
│   └── io_utils.py
├── scripts/
│   └── evaluate.py
├── tests/
│   ├── inputs.jsonl
│   └── expected_schema.json
├── app/
│   ├── __init__.py
│   └── app.py
├── .gitignore
└── LICENSE
```

## Support

1. For assignment-related questions, please consult **Assignment 1.pdf**.
2. For installing Ollama and pulling model, please see **INSTALL.md**.

## Framework Choice & Justification

This project uses **Streamlit** for the user interface and **Python** for backend logic and model integration.

- **Streamlit** was chosen for its simplicity, rapid prototyping capabilities, and interactive UI components. It allows for fast development of conversational interfaces and easy integration with Python code, making it ideal for building chatbots and data-driven applications.
- **Python** is used for backend logic, moderation, and model orchestration due to its rich ecosystem of machine learning libraries and straightforward integration with APIs such as OpenAI and Ollama.
- The modular structure (with separate files for moderation, model provider, and chat engine) ensures maintainability, extensibility, and clear separation of concerns.

This combination enables a robust, maintainable, and user-friendly psychological support chatbot that can be easily extended or adapted for future needs.


## Running Instructions

## Running on macOS
```bash
# Create Conda environment (Python 3.11)
conda create -n cs3249 python=3.11 -y
conda activate cs3249

# Install Python dependencies
pip install -r requirements.txt
```

This projet uses OpenAI API. Add your OpenAI API key to the top of `model_provider.py` file and run

```bash
# Run tests (See Assignment 1.pdf for details)
python scripts/evaluate.py
```

If you are using Ollama, then run the Ollama service in a seperate terminal

```bash
# In a separate terminal, start and keep the Ollama service running
ollama serve

# Run tests (See Assignment 1.pdf for details)
python scripts/evaluate.py
```

## Running on Windows

```bash
# Create Conda environment (Python 3.11)
conda create -n cs3249 python=3.11 -y
conda activate cs3249

# Install Python dependencies
pip install -r requirements.txt
```

This project uses OpenAI API. Add your OpenAI API key to the top of `model_provider.py` file and run

```bash
# Run tests (See Assignment 1.pdf for details)
python scripts\evaluate.py
```

If you are using Ollama, then run the Ollama service in a seperate Command Prompt or PowerShell window

```bash
# In a separate Command Prompt or PowerShell window, start and keep the Ollama service running
ollama serve

# Run tests (See Assignment 1.pdf for details)
python scripts\evaluate.py
```

## UI Design Decisions

### Safety-first Principles
The chatbot is designed to prioritize user safety at every step. Harmful or crisis-related user inputs are detected through robust moderation logic, and the bot responds by providing referral information for professional resources (such as helplines) without supporting unsafe requests. Medical advice and diagnoses are strictly blocked, ensuring the system never oversteps its boundaries.

### Accessibility Requirements
The interface uses high-contrast, light color schemes and simple, uncluttered layouts to maximize readability and ease of use for all users. Chat history is clearly separated, and all controls are accessible via keyboard and screen readers. Color-coded responses help users quickly identify important messages, especially during crisis situations.

### User Trust and Comfort
Empathy and non-judgmental support are central to the design, with warm colors and friendly icons reinforcing a welcoming atmosphere. System boundaries and limitations are communicated transparently through disclaimers and bot responses. User privacy is respected by not storing sensitive information beyond the session, and the bot consistently encourages users to seek professional help when needed.

### Clear Communication of System Boundaries
Disclaimers are prominently displayed in the sidebar and at the start of each session, making users aware of the chatbot’s limitations. The bot’s responses consistently remind users that it cannot provide medical advice or diagnoses, and refer users to professional resources when appropriate. This ensures users understand the scope of support provided and are guided toward safe, responsible next steps.