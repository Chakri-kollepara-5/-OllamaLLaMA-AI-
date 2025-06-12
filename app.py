import streamlit as st
import requests
import os
from datetime import datetime
import time

# --- Streamlit Page Config ---
st.set_page_config(
    page_title="Chakri's AI Assistant",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
st.markdown("""
    <style>
        /* Main Chat Container */
        .main {
            max-width: 800px !important;
        }
        
        /* Chat Messages */
        .stChatMessage {
            padding: 16px 20px;
            border-radius: 18px;
            margin-bottom: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            max-width: 80%;
            line-height: 1.5;
            font-size: 16px;
        }
        
        .stChatMessage.user {
            background-color: #f5f8ff;
            margin-left: auto;
            border-bottom-right-radius: 4px;
            border: 1px solid #e1e8ff;
        }
        
        .stChatMessage.assistant {
            background-color: #f9f9f9;
            margin-right: auto;
            border-bottom-left-radius: 4px;
            border: 1px solid #eaeaea;
        }
        
        /* Input Area */
        .stTextInput>div>div>input {
            border-radius: 24px !important;
            padding: 14px 18px !important;
            font-size: 16px !important;
        }
        
        /* Footer Position */
        .footer-container {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: white;
            padding: 10px 0;
            text-align: center;
            border-top: 1px solid #eee;
            z-index: 100;
        }
        
        .footer {
            font-size: 0.8em;
            color: #666;
            margin: 0 auto;
            max-width: 800px;
            padding: 0 20px;
        }
        
        /* Adjust chat container padding to prevent footer overlap */
        .stChatFadeIn {
            padding-bottom: 60px !important;
        }
        
        /* Modern Spinner */
        .spinner {
            width: 56px;
            height: 56px;
            display: grid;
            border: 4.5px solid #0000;
            border-radius: 50%;
            border-color: #dbdcef #0000;
            animation: spinner-e04l1k 1s infinite linear;
            margin: 0 auto;
        }
        
        .spinner::before,
        .spinner::after {
            content: "";
            grid-area: 1/1;
            margin: 2.2px;
            border: inherit;
            border-radius: 50%;
        }
        
        .spinner::before {
            border-color: #474bff #0000;
            animation: inherit;
            animation-duration: 0.5s;
            animation-direction: reverse;
        }
        
        .spinner::after {
            margin: 8.9px;
        }
        
        @keyframes spinner-e04l1k {
            100% {
                transform: rotate(1turn);
            }
        }
        
        .typing-indicator {
            display: flex;
            justify-content: center;
            padding: 20px 0;
        }
    </style>
""", unsafe_allow_html=True)

# --- Helper Functions ---
def query_llama3(prompt, history, model="llama3", temperature=0.7):
    """Function to call Ollama API"""
    url = "http://localhost:11434/api/chat"
    payload = {
        "model": model,
        "messages": history + [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {"temperature": temperature}
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()["message"]["content"]
        return f"❌ Error: API returned status code {response.status_code}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are Chakri's AI assistant. Be helpful, friendly, and offline."}
    ]
    
if "model" not in st.session_state:
    st.session_state.model = "llama3"
    
if "temperature" not in st.session_state:
    st.session_state.temperature = 0.7

# --- Sidebar Settings ---
with st.sidebar:
    st.title("⚙️ Settings")
    
    # Model Selection
    st.session_state.model = st.selectbox(
        "Model",
        ["llama3", "llama3-70b", "mistral", "phi3"],
        index=0
    )
    
    # Temperature Slider
    st.session_state.temperature = st.slider(
        "Creativeness",
        min_value=0.1,
        max_value=1.0,
        value=0.7,
        step=0.1
    )
    
    # Conversation Management
    st.markdown("---")
    st.markdown("### 💬 Conversation")
    if st.button("🧹 Clear Chat", use_container_width=True):
        st.session_state.messages = [
            {"role": "system", "content": "You are Chakri's AI assistant. Be helpful, friendly, and offline."}
        ]
        if os.path.exists("chat_log.txt"):
            os.remove("chat_log.txt")
        st.rerun()

# --- Main Chat Interface ---
st.title("💬 Chakri's AI Assistant")

# Display chat history
for message in st.session_state.messages[1:]:  # Skip system message
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
user_input = st.chat_input("Message AI Assistant...")

# Footer (positioned right below the input)
st.markdown("""
    <div class="footer-container">
        <div class="footer">
            Developed by Chakri • Powered by LLaMA 3 via Ollama
        </div>
    </div>
""", unsafe_allow_html=True)

# Handle user input after footer is rendered
if user_input:
    # Add user message to chat history and display immediately
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Display empty assistant message placeholder with spinner
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("""
            <div class="typing-indicator">
                <div class="spinner"></div>
            </div>
        """, unsafe_allow_html=True)
        
        # Get response from LLM
        reply = query_llama3(
            user_input, 
            st.session_state.messages[1:],
            model=st.session_state.model,
            temperature=st.session_state.temperature
        )
        
        # Display final message
        message_placeholder.markdown(reply)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": reply})
    
    # Save to file
    with open("chat_log.txt", "a", encoding="utf-8") as f:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{now}] User: {user_input}\n[{now}] Assistant: {reply}\n\n")