import os
import threading
from typing import Dict, List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# --- OpenAI new SDK (>= 1.0) ---
from openai import OpenAI

from config import (
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    OPENAI_MODEL,
    OPENAI_PORT
)

client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL
)

# ------------- FastAPI app -------------
app = FastAPI(title="CS3249 GPT Backend")

# Allow local frontends to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # for teaching/demo; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory session store: { session_id: [{"role": "...", "content": "..."}] }
SESSIONS: Dict[str, List[Dict[str, str]]] = {}

class ChatRequest(BaseModel):
    message: str
    temperature: float = 0.7
    max_tokens: int = 200
    history: List[Dict[str, str]] = []

class ChatResponse(BaseModel):
    response: str
    model: str

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    try:
        completion = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=req.history,
            temperature=req.temperature,
            max_tokens=req.max_tokens,
        )
        reply = completion.choices[0].message.content
        return ChatResponse(response=reply, model=OPENAI_MODEL)

    except Exception as e:
        # Surface error to the caller but keep JSON shape stable
        return ChatResponse(response=f"[Backend error: {e}]", model=OPENAI_MODEL)

def run_backend():
    uvicorn.run(app, host="0.0.0.0", port=OPENAI_PORT, log_level="info")

# Start once per Notebook execution
already_running = False
if 'thread' in globals():
    try:
        already_running = thread.is_alive()
    except Exception:
        already_running = False

if not already_running:
    thread = threading.Thread(target=run_backend, daemon=True)
    thread.start()

print(f"✅ GPT Backend running at http://localhost:{OPENAI_PORT}/chat")
print(f"   Model: {OPENAI_MODEL} | Base URL: {OPENAI_BASE_URL}")
thread.join()
