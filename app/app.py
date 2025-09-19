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

st.set_page_config(page_title="Mental Health Chatbot", page_icon="🧠", layout="centered")
st.title("Mental Health Chatbot 🧠")

# =============== Sidebar ===============
with st.sidebar:
    st.markdown("### Generation Params")
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1) # Low temperature leads to deterministic, focused and predictable outputs
    max_tokens = st.slider("Max Tokens", 10, 500, 200, 10)

    st.markdown("### Sessions")
    # Use a uuid-based session id for the initial session
    if "current_session" not in st.session_state:
        initial_id = f"sess-{uuid.uuid4().hex[:6]}"
        st.session_state.current_session = initial_id

    # Container that holds histories for all sessions:
    # Shape: { session_id: [ {role: "user"/"assistant", content: "..."} , ... ] }
    if "all_histories" not in st.session_state:
        st.session_state.all_histories = {st.session_state.current_session: []}

    # ----- UI controls for sessions -----
    session_ids = sorted(list(st.session_state.all_histories.keys()))
    selected = st.selectbox("Select session", options=session_ids,
                            index=session_ids.index(st.session_state.current_session)
                            if st.session_state.current_session in session_ids else 0)

    col1, col2 = st.columns(2)
    with col1:
        new_session_btn = st.button("➕ New session")
    with col2:
        clear_session_btn = st.button("🗑️ Clear current session")

    

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

def create_new_session() -> None:
    """
    Creates a new session_id (e.g., 'sess-xxxxxx') and adds an empty history list
    to st.session_state.all_histories, then sets st.session_state.current_session to the new id.
    """
    new_id = f"sess-{uuid.uuid4().hex[:6]}"
    st.session_state.all_histories[new_id] = []
    st.session_state.current_session = new_id


def switch_session(target_session_id: str) -> None:
    """
    Switches current session to `target_session_id`.
    """
    if target_session_id in st.session_state.all_histories:
        st.session_state.current_session = target_session_id
    else:
        st.warning(f"Session id '{target_session_id}' not found.")


def clear_current_session() -> None:
    """
    Clears the history of the current session.
    """
    st.session_state.all_histories[st.session_state.current_session] = []


def get_history() -> list[dict]:
    """
    Returns the history list for the *current* session.
    """
    return st.session_state.engine.get_conversation_history()


def append_turn(role: str, content: str, type: str) -> None:
    """
    Appends a message to the *current* session's history.
    """
    st.session_state.all_histories[st.session_state.current_session].append({"role": role, "content": content, "type": type})


# =============== Wire up session controls ===============
# Switch to selected session in the Selectbox
switch_session(selected)

if new_session_btn:
    create_new_session()

if clear_session_btn:
    clear_current_session()
    

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
            st.markdown(f"**You:** {msg['content']}")
    elif msg["role"] == "system":
        st.markdown(f"<div style='background-color:#f0f0f0;color:#000000;padding:8px;border-radius:8px;margin-bottom:4px;'>"
                    f"🛑 <b>System:</b> {msg['content']}" "</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='background-color:{style['color']};color:#000000;padding:8px;border-radius:8px;margin-bottom:4px;'>"
                    f"{style['icon']} <b>Bot:</b> {msg['content']}" "</div>", unsafe_allow_html=True)

# User input
with st.form(key="chat_form"):
    user_input = st.text_input("Type your message:", "", key="user_input")
    submitted = st.form_submit_button("Send")

if submitted:
    st.session_state.loading = True
    try:
        append_turn("user", user_input, "normal")
        with st.spinner("Bot is typing..."):
            response = get_bot_response(user_input)
        append_turn("assistant", response["response"], response["safety_action"])
    except Exception as e:
        st.session_state.error = f"Error: {str(e)}"
    st.session_state.loading = False
    st.rerun()
