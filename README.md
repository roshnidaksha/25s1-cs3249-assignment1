# Assignment 1: Building a Local LLM Psychological Pre-consultation Chatbot

## Project Overview

Mental health support systems play a critical role in providing accessible initial assistance to individuals seeking psychological help. This assignment tasks you with building a local LLM-based CUI for psychological pre-consultation. The system should provide empathetic listening, assess user needs, and appropriately refer users to professional resources when necessary.

**Important**: This system is for educational purposes only and should NOT provide diagnoses or treatment recommendations.

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

## Running on macOS

```bash
# Create Conda environment (Python 3.11)
conda create -n cs3249 python=3.11 -y
conda activate cs3249

# Install Python dependencies
pip install -r requirements.txt

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

# In a separate Command Prompt or PowerShell window, start and keep the Ollama service running
ollama serve

# Run tests (See Assignment 1.pdf for details)
python scripts\evaluate.py
```
