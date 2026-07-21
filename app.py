import streamlit as st

st.title("MULTIVERSE OF CHATBOT")

personality=st.sidebar.selectbox("who do you wanna talk to?",["an angry ravi shashtri ","donald trump", "a hacker","virat kohli"])


from google import genai
import os
from dotenv import load_dotenv
load_dotenv()

client=genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

user_message=st.text_input("say something : ")

if st.button("send"):
  if user_message:
      ai_instructions = f"""
you are acting as {personality}.
Respond to the message send by the user staying completely in character:
{user_message}
"""
      
      with st.spinner("connecting to the multiverse!..."):
          response=client.models.generate_content(
              model="gemini-3.5-flash",
              contents=ai_instructions
        )
          st.success("message received!")
          st.write(response.text)
          
  else:
      st.warning("please type a message first")
       
         