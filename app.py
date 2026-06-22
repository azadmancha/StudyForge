import streamlit as st
from groq import Groq
import os


# ---------- PAGE ----------
st.set_page_config(
    page_title="StudyForge",
    page_icon="⚒️",
    layout="wide"
)


# ---------- STYLE ----------
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
}

h1 {
    text-align: center;
}

.stButton button {
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)


# ---------- CLIENT ----------
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# ---------- MEMORY ----------
if "messages" not in st.session_state:
    st.session_state.messages = []


# ---------- SIDEBAR ----------
with st.sidebar:

    st.title("⚒️ StudyForge")

    st.caption("Your AI-powered learning workspace")

    subject = st.selectbox(
        "📚 Subject",
        ["Math", "Physics"]
    )

    depth = st.selectbox(
        "🧠 Learning Depth",
        [
            "Basic",
            "Standard",
            "Deep Dive"
        ]
    )

    exam_mode = st.toggle(
        "📝 Exam Mode"
    )

    hint_mode = st.toggle(
        "💡 Hint Mode"
    )

    st.divider()

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()



# ---------- HEADER ----------
st.title("⚒️ StudyForge")
st.caption("Understand. Practice. Improve.")



# ---------- DISPLAY OLD CHAT ----------
for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])



# ---------- USER INPUT ----------
question = st.chat_input(
    "Ask a Math or Physics question..."
)



# ---------- RESPONSE ----------
if question:

    # Show user question immediately
    with st.chat_message("user"):
        st.markdown(question)


    # Save user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )


    if hint_mode:
        answer_style = """
Give hints only.
Do not reveal the final answer unless requested.
"""
    else:
        answer_style = """
Give the complete solution.
"""


    if exam_mode:
        format_style = """
Use exam format:

Given:
Formula:
Working:
Final Answer:
"""
    else:
        format_style = """
Explain like a personal tutor.
"""


    prompt = f"""
You are StudyForge, an expert {subject} tutor.

Learning depth:
{depth}

Rules:
- Give accurate answers.
- Solve carefully.
- For numerical problems:
  - Write equations.
  - Substitute values.
  - Show calculations.
- Be careful with percentages, units, and algebra.
- Fix mistakes before responding.

Do not mention:
- checking
- verification
- internal reasoning

Math:
Use LaTeX formatting for equations.

Physics:
Include formulas and units.

{format_style}

{answer_style}

Make answers clear and student-friendly.
"""


    with st.chat_message("assistant"):

        with st.spinner("Thinking... ⚒️"):

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": prompt
                    },
                    {
                        "role": "user",
                        "content": question
                    }
                ]
            )


            answer = response.choices[0].message.content

            st.markdown(answer)


    # Save AI response
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
            )
