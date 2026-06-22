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


    st.subheader("📘 Formula Bank")

    if subject == "Math":

        st.write("""
**Algebra**
- (a+b)² = a²+2ab+b²
- Quadratic formula

**Geometry**
- Area
- Volume
- Pythagoras

**Trigonometry**
- sin, cos, tan
- identities

**Calculus**
- Derivatives
- Integration basics
""")


    else:

        st.write("""
**Mechanics**
- v=u+at
- F=ma
- Work Energy

**Waves**
- v=fλ

**Electricity**
- V=IR
- P=VI

**Optics**
- Lens formula
- Mirror formula
""")


    st.divider()


    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()



# ---------- HEADER ----------
st.title("⚒️ StudyForge")

st.caption(
    "Understand. Practice. Improve."
)


# ---------- CHAT ----------
for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])



# ---------- INPUT ----------
question = st.chat_input(
    "Ask a Math or Physics question..."
)



# ---------- AI ----------
if question:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )


    if hint_mode:
        output_style = """
Give hints only.
Do not give the final answer unless the user asks.
"""
    else:
        output_style = """
Give a complete solution.
"""


    if exam_mode:
        exam_style = """
Use exam format:
Given:
Formula:
Working:
Answer:
"""
    else:
        exam_style = """
Explain like a tutor.
"""


    prompt = f"""
You are StudyForge, an expert {subject} tutor.

Learning depth:
{depth}

Rules:
- Give accurate answers.
- Check calculations internally before replying.
- Fix mistakes before answering.
- Do not mention checking or internal reasoning.

Math:
- Use LaTeX for equations.

Physics:
- Include formulas and units.

{exam_style}

{output_style}

Be clear and student friendly.
"""


    with st.chat_message("assistant"):

        with st.spinner("Forging answer... ⚒️"):

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


    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )
