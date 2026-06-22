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
            "system_prompt = """
You are an expert Physics and Math tutor.

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
- Do NOT show any verification, checking process, corrections, or internal reasoning about mistakes.
- Do NOT mention re-checking or self-correction.

The response must be clean, professional, and exam-ready.
"""

response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question}
    ]
)": question
        }
    ]
)

answer = response.choices[0].message.content
st.write(answer)
