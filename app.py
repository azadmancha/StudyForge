import streamlit as st
from groq import Groq
import os

st.set_page_config(page_title="StudyForge", page_icon="⚒️")

st.title("StudyForge ⚒️")
st.write("AI Tutor for Math & Physics")

# Get API key from Streamlit secrets
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

question = st.text_input("Ask your question")

if question:
    with st.spinner("Thinking... ⚒️"):

        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful tutor. Explain step by step in simple language."
                },
                {
                    "role": "user",
                    "content": question
                }
            ]
        )

        answer = response.choices[0].message.content
        st.write(answer)
