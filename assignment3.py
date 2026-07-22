import streamlit as st
from google import genai
import os
from dotenv import load_dotenv

# Load the API key
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# App title
st.title("MULTIVERSE OF CHATBOT")

# Sidebar settings
st.sidebar.title("App Settings")

personality = st.sidebar.selectbox(
    "Choose a Personality",
    [
        "An Angry Man",
        "An Expert Hacker",
        "Virat Kohli",
        "A Panicked College Student at 3 AM",
        "A 1920s Mafia Boss",
        "A Sarcastic Fitness Coach"
    ]
)

intensity = st.sidebar.slider(
    "Intensity Level",
    1,
    10,
    5
)

# Create message history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:

    if message["role"] == "assistant":

        with st.chat_message("assistant", avatar=message["avatar"]):
            st.write(message["content"])

    else:

        with st.chat_message("user"):
            st.write(message["content"])

# Chat input
if user_message := st.chat_input("Say something..."):

    # Show user message
    with st.chat_message("user"):
        st.write(user_message)

    # Save user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    # Select avatar
    if personality == "An Expert Hacker":
        bot_avatar = "💻"

    elif personality == "Virat Kohli":
        bot_avatar = "🏏"

    elif personality == "A Sarcastic Fitness Coach":
        bot_avatar = "💪"

    elif personality == "A Panicked College Student at 3 AM":
        bot_avatar = "😰"

    elif personality == "A 1920s Mafia Boss":
        bot_avatar = "🕴️"

    else:
        bot_avatar = "😡"

    # AI instructions
    ai_instruction = f"""
    You are {personality}.

    Act with an intensity level of {intensity} out of 10.

    Reply according to your personality.
    """

    # Generate AI response
    with st.spinner("Generating response..."):

        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=f"{ai_instruction}\n\nUser: {user_message}"
        )

    # Show AI response
    with st.chat_message("assistant", avatar=bot_avatar):
        st.write(response.text)

    # Save AI response
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response.text,
            "avatar": bot_avatar
        }
    )