import streamlit as st
from openai import OpenAI
import os

st.title("⚒️ StudyForge")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

question = st.text_input("Ask your question")

if question:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful tutor. Explain step by step simply."},
            {"role": "user", "content": question}
        ]
    )

    st.write(response.choices[0].message.content)
