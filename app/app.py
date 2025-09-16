import streamlit as st
from typing import Dict
import sys
import os
# Ensure project root is in sys.path for module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.chat_engine import get_engine

# Initial disclaimer text
DISCLAIMER = """
**Disclaimer:** This chatbot is not a substitute for professional mental health advice, diagnosis, or treatment. If you are in crisis or need immediate help, please contact a mental health professional or emergency services.
"""

# Simulated backend response function
# Replace with actual backend integration
def get_bot_response(user_message: str) -> Dict:
    final_response = get_engine().process_message(user_message)
    type_map = {
        "allow": "normal",
        "block": "blocked",
        "safe_fallback": "fallback"
    }
    return {
        "text": final_response["response"],
        "type": type_map.get(final_response["safety_action"], "normal")
    }
    
# Visual indicator styles
RESPONSE_STYLES = {
    "normal": {"color": "#e0ffe0", "icon": "💬"},
    "blocked": {"color": "#ffe0e0", "icon": "⛔"},
    "fallback": {"color": "#fffbe0", "icon": "⚠️"},
}

# Session state for conversation
if "history" not in st.session_state:
    st.session_state.history = []
if "disclaimer_ack" not in st.session_state:
    st.session_state.disclaimer_ack = False
if "loading" not in st.session_state:
    st.session_state.loading = False
if "error" not in st.session_state:
    st.session_state.error = ""

st.set_page_config(page_title="Mental Health Chatbot", page_icon="🧠", layout="centered")

# Disclaimer modal
if not st.session_state.disclaimer_ack:
    st.markdown(DISCLAIMER)
    if st.button("I Understand and Wish to Continue"):
        st.session_state.disclaimer_ack = True
    st.stop()

st.title("Mental Health Chatbot 🧠")

# Show error if any
if st.session_state.error:
    st.error(st.session_state.error)
    st.session_state.error = ""

# Conversation history
st.subheader("Conversation History")
for msg in st.session_state.history:
    style = RESPONSE_STYLES.get(msg["type"], RESPONSE_STYLES["normal"])
    if msg["sender"] == "user":
        st.markdown(f"**You:** {msg['text']}")
    else:
        st.markdown(f"<div style='background-color:{style['color']};color:#000000;padding:8px;border-radius:8px;margin-bottom:4px;'>"
                    f"{style['icon']} <b>Bot:</b> {msg['text']}" "</div>", unsafe_allow_html=True)

# User input
with st.form(key="chat_form"):
    user_input = st.text_input("Type your message:", "", key="user_input")
    submitted = st.form_submit_button("Send")

if submitted:
    st.session_state.loading = True
    try:
        st.session_state.history.append({"sender": "user", "text": user_input, "type": "normal"})
        # Simulate loading state
        with st.spinner("Bot is typing..."):
            response = get_bot_response(user_input)
        st.session_state.history.append({"sender": "bot", "text": response["text"], "type": response["type"]})
    except Exception as e:
        st.session_state.error = f"Error: {str(e)}"
    st.session_state.loading = False
    st.rerun()
