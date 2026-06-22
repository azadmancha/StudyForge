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
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "system",
            "content": """
You are an expert physics and math tutor.

You MUST follow this format:

1. Solve the problem step by step.
2. Give final answer clearly.
3. Then RE-CHECK your solution:
   - verify calculations
   - verify logic
   - correct mistakes if any

If you find an error, fix it before final output.
"""
        },
        {
            "role": "user",
            "content": question
        }
    ]
)

answer = response.choices[0].message.content
st.write(answer)
