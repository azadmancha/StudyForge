import streamlit as st
from groq import Groq
import os


# ---------- PAGE ----------
st.set_page_config(
    page_title="StudyForge",
    page_icon="⚒️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ---------- UI STYLE ----------
st.markdown("""
<style>

.block-container {
    padding-top: 1.5rem;
}


/* Hide default chat avatars */
[data-testid="stChatMessageAvatar"] {
    display: none;
}


/* Chat cards */
.user-card {
    background: #2b2b2b;
    color: white;
    padding: 14px;
    border-radius: 18px;
    margin-left: 25%;
    margin-bottom: 10px;
}


.ai-card {
    background: #161616;
    color: #f5f5f5;
    padding: 14px;
    border-radius: 18px;
    margin-right: 25%;
    margin-bottom: 10px;
    border: 1px solid #333;
}


.stButton button {
    border-radius: 12px;
}

</style>
""", unsafe_allow_html=True)



# ---------- CLIENT ----------
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)



# ---------- MEMORY ----------
if "messages" not in st.session_state:
    st.session_state.messages = []



# ---------- SIDEBAR ----------
with st.sidebar:

    st.title("⚒️ StudyForge")

    st.caption(
        "Your AI learning workspace"
    )


    if st.button("◀ Collapse Sidebar"):

        st.markdown(
            """
            <script>
            window.parent.document
            .querySelector('[data-testid="stSidebarCollapseButton"]')
            .click();
            </script>
            """,
            unsafe_allow_html=True
        )


    st.divider()


    subject = st.selectbox(
        "Subject",
        [
            "Math",
            "Physics"
        ]
    )


    depth = st.selectbox(
        "Learning Depth",
        [
            "Basic",
            "Standard",
            "Deep Dive"
        ]
    )


    exam_mode = st.toggle(
        "Exam Mode"
    )


    hint_mode = st.toggle(
        "Hint Mode"
    )


    st.divider()


    if st.button("Clear Chat"):

        st.session_state.messages = []
        st.rerun()



# ---------- HEADER ----------
st.title("⚒️ StudyForge")

st.caption(
    "Understand. Practice. Improve."
)



# ---------- LATEX ----------
def show_message(text):

    parts = text.split("$$")

    for i, part in enumerate(parts):

        if i % 2 == 1:
            st.latex(part)

        else:
            st.markdown(part)



# ---------- CHAT HISTORY ----------
for message in st.session_state.messages:


    if message["role"] == "user":

        st.markdown(
            f"""
            <div class="user-card">
            {message["content"]}
            </div>
            """,
            unsafe_allow_html=True
        )


    else:

        st.markdown(
            """
            <div class="ai-card">
            """,
            unsafe_allow_html=True
        )

        show_message(
            message["content"]
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )



# ---------- INPUT ----------
question = st.chat_input(
    "Ask a question..."
)



# ---------- AI ----------
if question:


    st.markdown(
        f"""
        <div class="user-card">
        {question}
        </div>
        """,
        unsafe_allow_html=True
    )


    st.session_state.messages.append(
        {
            "role":"user",
            "content":question
        }
    )


    if hint_mode:

        answer_style = """
Give hints only.
Do not give final answer.
"""

    else:

        answer_style = """
Give full solution.
"""


    if exam_mode:

        format_style = """
Use:

Given:
Formula:
Steps:
Answer:
"""

    else:

        format_style = """
Teach clearly.
"""



    prompt = f"""

You are StudyForge, an expert {subject} tutor.

Depth:
{depth}

Rules:
- Be accurate.
- Show equations.
- Show calculations.
- Fix mistakes before replying.
- Use LaTeX with $$ symbols.

Do not mention internal checking.

{format_style}

{answer_style}

"""



    with st.spinner(
        "Thinking..."
    ):

        response = client.chat.completions.create(

            model="llama-3.1-8b-instant",

            messages=[

                {
                    "role":"system",
                    "content":prompt
                },

                {
                    "role":"user",
                    "content":question
                }

            ]

        )


        answer = response.choices[0].message.content



    st.markdown(
        """
        <div class="ai-card">
        """,
        unsafe_allow_html=True
    )

    show_message(answer)

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


    st.session_state.messages.append(
        {
            "role":"assistant",
            "content":answer
        }
    )
