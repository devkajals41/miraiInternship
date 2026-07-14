import os
import streamlit as st
from dotenv import load_dotenv
from personas import PERSONAS
import google.generativeai as genai

# Configure Gemini API
# Load variables from .env file
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("Gemini API key not found. Please check your .env file.")
    st.stop()

genai.configure(api_key=api_key)

# Load Gemini model
model = genai.GenerativeModel("models/gemini-flash-latest")

# Basic page settings
st.set_page_config(
    page_title="🌌 Multiverse Chatbot",
    page_icon="🌌",
    layout="centered"
)

st.title("🌌 Multiverse Chatbot")

# Let the user choose a chatbot personality
selected_persona = st.selectbox(
    "Choose a Persona",
    list(PERSONAS.keys())
)

st.info(PERSONAS[selected_persona]["description"])

# Create chat history only once
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show all previous messages whenever the app reruns
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Wait for the user to type a new message
if user_message := st.chat_input("Say something..."):

    # Store the user's message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    # Display the user's message immediately
    with st.chat_message("user"):
        st.markdown(user_message)

    # Prepare the prompt for Gemini
    prompt = f"""
    You are acting as {selected_persona}.

    Personality:
    {PERSONAS[selected_persona]["description"]}

    User:
    {user_message}
    """

    # Generate AI response
    response = model.generate_content(prompt)

    # Show Gemini's reply
    with st.chat_message("assistant"):
        st.markdown(response.text)

    # Save the AI response so it stays after reruns
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response.text
        }
    )