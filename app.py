import streamlit as st
import requests
import os
from datetime import datetime
import time
import pytz
from streamlit.components.v1 import html
import base64
from typing import Generator
import json
from PIL import Image

# --- Page Configuration ---
st.set_page_config(
    page_title="Chakri's AI Assistant",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- Custom CSS for Advanced UI ---
st.markdown("""
    <style>
        .main {
            max-width: 900px !important;
            padding-bottom: 50px;
        }
        .stChatMessage {
            padding: 12px 16px;
            border-radius: 18px;
            margin-bottom: 8px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            max-width: 85%;
        }
        .stChatMessage.user {
            background-color: #f0f7ff;
            margin-left: auto;
            border-bottom-right-radius: 4px;
        }
        .stChatMessage.assistant {
            background-color: #f8f9fa;
            margin-right: auto;
            border-bottom-left-radius: 4px;
        }
        .stTextInput>div>div>input {
            border-radius: 24px !important;
            padding: 12px 16px !important;
        }
        .stButton>button {
            border-radius: 20px !important;
            padding: 8px 16px !important;
        }
        .typing-indicator {
            display: inline-flex;
            align-items: center;
        }
        .typing-dot {
            width: 8px;
            height: 8px;
            background-color: #6c757d;
            border-radius: 50%;
            margin: 0 2px;
            animation: blink 1.4s infinite both;
        }
        .typing-dot:nth-child(2) { animation-delay: 0.2s; }
        .typing-dot:nth-child(3) { animation-delay: 0.4s; }
        @keyframes blink {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        .welcome-message {
            animation: fadeIn 0.8s ease-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "first_visit" not in st.session_state:
    st.session_state.first_visit = True
if "model" not in st.session_state:
    st.session_state.model = "mistral"
if "temperature" not in st.session_state:
    st.session_state.temperature = 0.7
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# --- Helper Functions ---
def get_greeting():
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Good morning"
    elif 12 <= hour < 17:
        return "Good afternoon"
    elif 17 <= hour < 22:
        return "Good evening"
    else:
        return "Good night"

def typing_animation():
    return """
    <div class="typing-indicator">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
    </div>
    """

def get_current_time():
    return datetime.now().strftime("%I:%M %p")

def query_huggingface(prompt):
    headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"}
    API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"

    payload = {
        "inputs": prompt,
        "parameters": {"temperature": st.session_state.temperature, "max_new_tokens": 250}
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    result = response.json()

    try:
        return result[0]["generated_text"]
    except:
        return "⚠️ Error generating response. The model may be warming up."

# --- Welcome Message ---
if st.session_state.first_visit:
    greeting = get_greeting()
    current_time = get_current_time()
    st.markdown(f"""
        <div class="welcome-message">
            <h3>{greeting}! I'm Chakri's HuggingFace Assistant 🤖</h3>
            <p>It's currently {current_time}. How can I help you today?</p>
            <p><small>Try asking me anything or use the sidebar to customize your experience.</small></p>
        </div>
    """, unsafe_allow_html=True)
    st.session_state.first_visit = False

# --- Sidebar Settings ---
with st.sidebar:
    st.title("⚙️ Settings")
    st.session_state.temperature = st.slider("Creativity (Temperature)", 0.1, 1.0, 0.7, 0.1)
    st.session_state.dark_mode = st.toggle("Dark Mode", value=False)
    st.markdown("---")
    st.markdown("### 📝 Conversation History")
    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    if st.button("💾 Export Chat"):
        if st.session_state.messages:
            chat_text = "\n".join(f"{msg['role'].capitalize()}: {msg['content']}" for msg in st.session_state.messages)
            st.download_button(
                label="Download Chat",
                data=chat_text,
                file_name=f"chat_history_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )
        else:
            st.warning("No conversation to export")

# --- Main Chat Interface ---
st.title("💬 Chakri's AI Assistant")

# Display messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Message Chakri's AI..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for chunk in prompt.split():
            full_response += chunk + " "
            time.sleep(0.05)
            message_placeholder.markdown(full_response + typing_animation(), unsafe_allow_html=True)
        response = query_huggingface(prompt)
        message_placeholder.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

# --- Feature Highlights ---
st.markdown("---")
st.markdown("### ✨ Features")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.markdown("**🌙 Dark Mode**<br><small>Toggle theme style</small>", unsafe_allow_html=True)
with col2:
    st.markdown("**🧠 Persistent Memory**<br><small>Session-based chat</small>", unsafe_allow_html=True)
with col3:
    st.markdown("**💾 Export Chat**<br><small>Save conversations</small>", unsafe_allow_html=True)
with col4:
    st.markdown("**🧹 Clear All**<br><small>Start fresh anytime</small>", unsafe_allow_html=True)
with col5:
    st.markdown("**🤗 Hugging Face API**<br><small>Powerful LLM</small>", unsafe_allow_html=True)

# --- Footer ---
st.markdown(f"""
    <div style="text-align: center; margin-top: 50px; color: #6c757d; font-size: 0.9em;">
        <p>Powered by Hugging Face • Made with ❤️ by Chakri</p>
        <p>Last updated: {datetime.now().strftime('%Y-%m-%d')}</p>
    </div>
""", unsafe_allow_html=True)

# --- Dark Mode Script ---
if st.session_state.dark_mode:
    st.markdown("""
        <script>
            document.body.style.backgroundColor = "#0e1117";
            document.body.style.color = "#f8f9fa";
        </script>
    """, unsafe_allow_html=True)
