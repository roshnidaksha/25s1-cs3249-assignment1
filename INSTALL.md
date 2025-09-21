# Installation Guide

## Prerequisites

- Python 3.11
- 8GB RAM (minimum)
- 10GB free disk space
- Internet connection for initial setup

## macOS Installation

### Step 1: Install Python (if needed)

```bash
# Check Python version
python3 --version

# If Python 3.10+ not installed, use Homebrew:
brew install python@3.11
```

Follow steps 2 to 5 only if using Ollama model. If you are using OpenAI API key, the following steps are not necessary.

### Step 2: Install Ollama (Primary Method)

```bash
# Install using Homebrew
brew install ollama

# Or download from official website:
# https://ollama.ai/download/mac
```

### Step 3: Start Ollama Service

```bash
# Start Ollama in the background (keep it open)
ollama serve

# Verify it's running (in a new terminal!)
ollama list
```

### Step 4: Pull the Model

```bash
# Pull Phi-3 Mini (recommended, ~2.3GB)
ollama pull phi3:mini
```

### Step 5: Verify Installation

```bash
# Test model is available
ollama run phi3:mini "Hello, how are you?"

# Exit with /bye
```

## Windows Installation

### Step 1: Install Python

1. Download Python 3.11 from https://python.org
2. **Important**: Check "Add Python to PATH" during installation
3. Verify in PowerShell:

```powershell
python --version
```

Follow steps 2 and 3 only if using Ollama model. If you are using OpenAI API key, the following steps are not necessary.

### Step 2: Install Ollama

1. Download installer from: https://ollama.ai/download/windows
2. Run the installer (OllamaSetup.exe)
3. Ollama will start automatically and appear in system tray

### Step 3: Pull the Model

Open PowerShell and run:

```bash
# Pull Phi-3 Mini
ollama pull phi3:mini

# Test it works
ollama run phi3:mini "Hello"
# Type /bye to exit
```

## Troubleshooting

### Ollama Connection Errors

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
# macOS:
brew services restart ollama
# Windows: 
# Right-click system tray icon → Quit, then restart

# Check port isn't blocked
lsof -i :11434  # macOS
netstat -an | findstr :11434  # Windows
```

### Model Download Issues

```bash
# Clear Ollama cache and retry
ollama rm phi3:mini
ollama pull phi3:mini

# Try with --insecure flag if certificate issues
ollama pull phi3:mini --insecure
```