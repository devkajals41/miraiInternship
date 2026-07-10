import streamlit as st
from personas import PERSONAS

st.set_page_config(
    page_title="Multiverse Chatbot",
    page_icon="🌌",
    layout="centered"
)

st.title("🌌 Multiverse Chatbot")

selected_persona = st.selectbox(
    "Choose a Persona",
    list(PERSONAS.keys())
)

st.info(PERSONAS[selected_persona]["description"])

user_input = st.text_input("Ask something...")

if st.button("Send"):
    st.success(f"You selected: {selected_persona}")
    st.write("User:", user_input)