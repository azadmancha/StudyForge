import streamlit as st
import sqlite3
from groq import Groq


# ----------------------
# Setup
# ----------------------

st.set_page_config(
    page_title="StudyForge AI",
    page_icon="⚒️",
    layout="wide"
)


client = Groq(
    api_key=st.secrets["GROQ_API_KEY"]
)


# ----------------------
# Database
# ----------------------

db = sqlite3.connect(
    "studyforge.db",
    check_same_thread=False
)

cursor = db.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS messages(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT,
    content TEXT
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS feedback(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    response TEXT,
    rating TEXT
)
""")

db.commit()



def save_message(role, content):

    cursor.execute(
        "INSERT INTO messages(role,content) VALUES (?,?)",
        (role, content)
    )

    db.commit()



def get_messages():

    cursor.execute(
        "SELECT role,content FROM messages ORDER BY id"
    )

    return cursor.fetchall()



def save_feedback(response, rating):

    cursor.execute(
        "INSERT INTO feedback(response,rating) VALUES (?,?)",
        (response, rating)
    )

    db.commit()



# ----------------------
# AI Logic
# ----------------------

def detect_subject(text):

    text = text.lower()

    if any(word in text for word in [
        "equation",
        "algebra",
        "solve",
        "math"
    ]):
        return "Math"

    if any(word in text for word in [
        "force",
        "energy",
        "velocity",
        "physics"
    ]):
        return "Physics"

    return "General"



def create_prompt(
    question,
    subject,
    difficulty,
    mode
):

    return f"""
You are StudyForge AI Tutor.

Subject: {subject}
Difficulty: {difficulty}
Mode: {mode}

Instructions:
- Teach clearly
- Explain step by step
- Do not just give answers
- Adapt to the student's level

Question:
{question}
"""



def ask_ai(prompt):

    response = client.chat.completions.create(

        model="llama3-70b-8192",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.4
    )

    return response.choices[0].message.content



# ----------------------
# Sidebar
# ----------------------

with st.sidebar:

    st.title("⚒️ StudyForge")

    difficulty = st.selectbox(
        "Difficulty",
        [
            "Easy",
            "Normal",
            "Advanced"
        ]
    )


    mode = st.selectbox(
        "Mode",
        [
            "Normal",
            "Exam",
            "Hint"
        ]
    )


    if st.button("Clear History"):

        cursor.execute(
            "DELETE FROM messages"
        )

        db.commit()

        st.rerun()



# ----------------------
# Main UI
# ----------------------

st.title("⚒️ StudyForge AI")

st.caption(
    "Your adaptive AI study assistant"
)



# Display old messages

for role, message in get_messages():

    with st.chat_message(role):

        st.markdown(message)



question = st.chat_input(
    "Ask your question..."
)



if question:

    save_message(
        "user",
        question
    )


    with st.chat_message("user"):
        st.markdown(question)


    subject = detect_subject(question)


    prompt = create_prompt(
        question,
        subject,
        difficulty,
        mode
    )


    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            answer = ask_ai(prompt)


        st.markdown(answer)


        col1, col2 = st.columns(2)


        with col1:

            if st.button(
                "👍 Helpful",
                key="good"
            ):

                save_feedback(
                    answer,
                    "positive"
                )

                st.success("Saved")


        with col2:

            if st.button(
                "👎 Improve",
                key="bad"
            ):

                save_feedback(
                    answer,
                    "negative"
                )

                st.warning("Saved")


    save_message(
        "assistant",
        answer
    )
