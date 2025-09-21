import streamlit as st
from typing import Dict
import logging
import uuid
import sys
import os
# Ensure project root is in sys.path for module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.chat_engine import get_engine

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Visual indicator styles
RESPONSE_STYLES = {
    "allow": {"color": "#e0ffe0", "icon": "💬"},
    "block": {"color": "#ffe0e0", "icon": "⛔"},
    "safe_fallback": {"color": "#fffbe0", "icon": "⚠️"},
}

st.set_page_config(page_title="Psychological Pre-Consultation Bot", page_icon="🧠", layout="centered")
st.title("Psychological Pre-Consultation Bot 🧠")

# =============== Sidebar ===============
with st.sidebar:
    st.markdown("### Disclaimer")
    st.markdown("This AI chatbot provides only general emotional support and is not a substitute for professional care. It cannot diagnose, prescribe, or offer medical advice. If you are in crisis or need urgent help, please contact emergency services.")
    st.markdown("---")
    st.markdown("### Model Parameters")
    temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1) # Low temperature leads to deterministic, focused and predictable outputs
    max_tokens = st.slider("Max Tokens", min_value=10, max_value=500, value=200, step=10)

# Session state for conversation
if "loading" not in st.session_state:
    st.session_state.loading = False
if "error" not in st.session_state:
    st.session_state.error = ""
if "engine" not in st.session_state:
    st.session_state.engine = get_engine()
    _ = st.session_state.engine.process_message("") # Initialize disclaimer

# Track previous sidebar values for temperature and max_tokens
if "prev_temperature" not in st.session_state:
    st.session_state.prev_temperature = temperature
if "prev_max_tokens" not in st.session_state:
    st.session_state.prev_max_tokens = max_tokens

# Only update engine parameters if changed
if temperature != st.session_state.prev_temperature:
    st.session_state.engine.set_model_temperature(temperature)
    st.session_state.prev_temperature = temperature

if max_tokens != st.session_state.prev_max_tokens:
    st.session_state.engine.set_model_max_tokens(max_tokens)
    st.session_state.prev_max_tokens = max_tokens


# =============== Helpers ===============
def get_bot_response(user_message: str) -> Dict:
    final_response = st.session_state.engine.process_message(user_message, include_context=True)
    return final_response

def get_history() -> list[dict]:
    """
    Returns the history list for the *current* session.
    """
    return st.session_state.engine.get_conversation_history()

def show_to_user(msg: Dict, role: str):
    if role == "user":
        if msg['content'] != "DISCLAIMER_INIT":
            st.markdown(f"<div style='background-color:#e6f0ff;color:#000000;padding:8px;border-radius:8px;"
                        f"border:2px solid #b3c6e6;margin-bottom:16px;'>"
                        f"<b>🧑 You:</b> {msg['content']}" "</div>", unsafe_allow_html=True)
    elif role == "system":
        st.markdown(f"<div style='background-color:#f0f0f0;color:#000000;padding:8px;border-radius:8px;margin-bottom:16px;'>"
                    f"🛑 <b>System:</b> {msg['content']}" "</div>", unsafe_allow_html=True)
    else:
        style = RESPONSE_STYLES.get(msg["type"], RESPONSE_STYLES["allow"])
        st.markdown(f"<div style='background-color:{style['color']};color:#000000;padding:8px;border-radius:8px;margin-bottom:4px;'>"
                    f"{style['icon']} <b>Bot:</b> {msg['content']}" "</div>", unsafe_allow_html=True)
        if msg['turn_count'] != 0:
            st.markdown(
                f"<div style='font-size:12px;color:#888;margin-top:0px;margin-bottom:32px;'>"
                f"Safety: <b>{msg['type']}</b> &nbsp;|&nbsp; Latency: <b>{msg['latency_ms']} ms</b> &nbsp;|&nbsp; Turn: <b>{msg['turn_count']}</b>"
                "</div>",
                unsafe_allow_html=True
            )
    
# Show error if any
if st.session_state.error:
    st.error(st.session_state.error)
    st.session_state.error = ""

# =============== Layout: Chat (left) & Analytics (right) ===============
left, right = st.columns([2, 1])

    
# Conversation history
st.subheader("Conversation History")
for msg in get_history():
    style = RESPONSE_STYLES.get(msg["type"], RESPONSE_STYLES["allow"])
    if msg["role"] == "user":
        if msg["content"] != "DISCLAIMER_INIT":
            show_to_user(msg, "user")
    elif msg["role"] == "system":
        show_to_user(msg, "system")
    else:
        show_to_user(msg, "bot")

# User input        
if prompt := st.chat_input("Type your message here..."):
    show_to_user({"content": prompt}, "user")
    st.session_state.loading = True
    try:
        with st.spinner("Bot is typing..."):
            response = get_bot_response(prompt)
    except Exception as e:
        st.session_state.error = f"Error: {str(e)}"
    st.session_state.loading = False
    st.rerun()
