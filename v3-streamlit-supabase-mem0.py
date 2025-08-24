import os
import streamlit as st
from dotenv import load_dotenv
from mem0 import Memory
from supabase import create_client, Client # Corrected import
from pathlib import Path

# --- Load Environment Variables ---
project_root = Path(__file__).resolve().parent
dotenv_path = project_root / '.env'
load_dotenv(dotenv_path, override=True)

# --- Initialize Supabase Client (Corrected Initialization) ---
supabase_url = os.environ.get("SUPABASE_URL", "")
supabase_key = os.environ.get("SUPABASE_KEY", "")
supabase_client: Client = create_client(supabase_url, supabase_key)

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="Local AI Chat Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Cache the Memory Instance ---
@st.cache_resource
def get_memory():
    config = {
        "vector_store": {
            "provider": "supabase",
            "config": {
                "connection_string": os.environ['DATABASE_URL'],
                "collection_name": "memories",
                "embedding_model_dims": 768
            }
        },
        "llm": {
            "provider": "ollama",
            "config": {
                "model": "qwen3:8b",
                "ollama_base_url": "http://localhost:11434",
            },
        },
        "embedder": {
            "provider": "ollama",
            "config": {
                "model": "nomic-embed-text",
                "ollama_base_url": "http://localhost:11434",
            },
        },
    }
    return Memory.from_config(config)

# Get the cached memory instance
memory = get_memory()

# --- Authentication Functions ---
def sign_up(email, password, full_name):
    try:
        response = supabase_client.auth.sign_up({
            "email": email,
            "password": password,
            "options": {"data": {"full_name": full_name}}
        })
        if response and response.user:
            st.session_state.authenticated = True
            st.session_state.user = response.user
            st.rerun()
        return response
    except Exception as e:
        st.error(f"Error signing up: {str(e)}")
        return None

def sign_in(email, password):
    try:
        response = supabase_client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        if response and response.user:
            st.session_state.authenticated = True
            st.session_state.user = response.user
            st.rerun()
        return response
    except Exception as e:
        st.error(f"Error signing in: {str(e)}")
        return None

def sign_out():
    try:
        supabase_client.auth.sign_out()
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.messages = []
        st.session_state.logout_requested = True
    except Exception as e:
        st.error(f"Error signing out: {str(e)}")

# --- Chat Function ---
def chat_with_memories(message, user_id):
    with st.spinner("Thinking..."):
        relevant_memories = memory.search(query=message, user_id=user_id, limit=3)
        
        if relevant_memories and relevant_memories.get("results"):
            memories_str = "\n".join(f"- {entry['memory']}" for entry in relevant_memories["results"])
            system_prompt = f"You are a helpful AI. Answer based on the query and memories.\n\nMemories:\n{memories_str}"
        else:
            system_prompt = "You are a helpful AI."

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
        
        assistant_response = memory.llm.generate_response(messages=messages)
        
        messages.append({"role": "assistant", "content": assistant_response})
        memory.add(messages, user_id=user_id)

    return assistant_response

# --- Initialize Streamlit Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None
if "logout_requested" in st.session_state and st.session_state.logout_requested:
    st.session_state.logout_requested = False
    st.rerun()

# --- Sidebar and Main UI ---
with st.sidebar:
    st.title("🧠 Local AI Chat")
    if not st.session_state.authenticated:
        # Authentication UI
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        with tab1:
            st.subheader("Login")
            login_email = st.text_input("Email", key="login_email")
            login_password = st.text_input("Password", type="password", key="login_password")
            if st.button("Login"):
                if login_email and login_password:
                    sign_in(login_email, login_password)
                else:
                    st.warning("Please enter both email and password.")
        with tab2:
            st.subheader("Sign Up")
            signup_email = st.text_input("Email", key="signup_email")
            signup_password = st.text_input("Password", type="password", key="signup_password")
            signup_name = st.text_input("Full Name", key="signup_name")
            if st.button("Sign Up"):
                if signup_email and signup_password and signup_name:
                    sign_up(signup_email, signup_password, signup_name)
                else:
                    st.warning("Please fill in all fields.")
    else:
        # Logged-in user UI
        user = st.session_state.user
        if user:
            st.success(f"Logged in as: {user.email}")
            st.button("Logout", on_click=sign_out)
            st.subheader("Memory Management")
            if st.button("Clear All Memories"):
                memory.clear(user_id=user.id)
                st.success("All memories cleared!")
                st.session_state.messages = []
                st.rerun()

if st.session_state.authenticated and st.session_state.user:
    # Main chat interface
    st.title("Chat with Your Local AI")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    if user_input := st.chat_input("Type your message here..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
        
        ai_response = chat_with_memories(user_input, st.session_state.user.id)
        
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        with st.chat_message("assistant"):
            st.write(ai_response)
else:
    # Welcome screen
    st.title("Welcome to Your Local Chat Assistant")
    st.write("Please login or sign up to start a conversation.")