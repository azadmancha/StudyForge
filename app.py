import streamlit as st
from groq import Groq
import os

st.set_page_config(page_title="StudyForge", page_icon="⚒️")

st.title("StudyForge ⚒️")
st.write("AI Tutor for Math & Physics")

# API client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# System prompt (FIXED)
system_prompt = """You are an expert Physics and Math tutor.

Your job is to give accurate, clear, exam-quality solutions.

RULES:
1. Solve step by step in a clear and structured way.
2. Be careful with arithmetic, algebra, units, and percentage conversions.
3. Convert all percentages correctly before calculation.
4. Ensure logical consistency in every step.
5. Internally verify all calculations and reasoning before giving the final answer.
6. If any mistake is found during reasoning, correct it silently before responding.

OUTPUT RULES:
- Show step-by-step solution clearly.
- Provide the final answer clearly at the end.
- Do NOT show any verification or internal reasoning.
- Do NOT mention re-checking or self-correction.
"""

question = st.text_input("Ask your question")

if question:
    with st.spinner("Thinking... ⚒️"):

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ]
        )

        answer = response.choices[0].message.content
        st.write(answer)
