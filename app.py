import streamlit as st
import sqlite3
from groq import Groq
import datetime

# =========================
# CONFIG
# =========================

st.set_page_config(page_title="StudyForge AI", layout="wide")

client = Groq(api_key="YOUR_GROQ_API_KEY")

# =========================
# DATABASE
# =========================

conn = sqlite3.connect("studyforge.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT,
    message TEXT,
    timestamp TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message TEXT,
    feedback TEXT,
    timestamp TEXT
)
""")

conn.commit()

# =========================
# UTILS
# =========================

def save_chat(role, message):
    c.execute(
        "INSERT INTO chat_history (role, message, timestamp) VALUES (?, ?, ?)",
        (role, message, str(datetime.datetime.now()))
    )
    conn.commit()

def load_chat():
    c.execute("SELECT role, message FROM chat_history")
    return c.fetchall()

def save_feedback(message, fb):
    c.execute(
        "INSERT INTO feedback (message, feedback, timestamp) VALUES (?, ?, ?)",
        (message, fb, str(datetime.datetime.now()))
    )
    conn.commit()

# =========================
# SUBJECT DETECTION (SIMPLE)
# =========================

def detect_subject(q):
    q = q.lower()
    if any(x in q for x in ["x=", "solve", "equation", "math"]):
        return "Math"
    elif any(x in q for x in ["force", "energy", "physics", "acceleration"]):
        return "Physics"
    else:
        return "General"

# =========================
# PROMPT ENGINE
# =========================

def build_prompt(question, subject, difficulty, mode):

    base = f"""
You are StudyForge AI Tutor.

Rules:
- Subject: {subject}
- Difficulty: {difficulty}
- Mode: {mode}

Always:
- Explain step by step
- Be clear and structured
- Use simple language when needed
"""

    if mode == "Exam Mode":
        base += "\nFormat: Answer like a school exam solution."

    if mode == "Hint Mode":
        base += "\nGive hints first, not full solution."

    return base + f"\n\nQuestion: {question}"

# =========================
# AI CALL
# =========================

def get_ai_response(prompt):
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )
    return response.choices[0].message.content

# =========================
# SIDEBAR
# =========================

st.sidebar.title("⚒️ StudyForge Controls")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Advanced"]
)

mode = st.sidebar.selectbox(
    "Mode",
    ["Normal Mode", "Exam Mode", "Hint Mode"]
)

st.sidebar.markdown("---")

if st.sidebar.button("🧹 Clear Chat"):
    c.execute("DELETE FROM chat_history")
    conn.commit()
    st.rerun()

# =========================
# MAIN UI
# =========================

st.title("⚒️ StudyForge AI (V1.5)")
st.caption("Your adaptive AI learning tutor")

# Load chat
chat = load_chat()

# Display chat history FIRST (FIXED ISSUE)
for role, msg in chat:
    with st.chat_message(role):
        st.markdown(msg)

# Input
question = st.chat_input("Ask your question...")

if question:

    subject = detect_subject(question)

    prompt = build_prompt(
        question,
        subject,
        difficulty,
        mode
    )

    answer = get_ai_response(prompt)

    # Save user message
    save_chat("user", question)

    # Save AI response
    save_chat("assistant", answer)

    # Display immediately
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        st.markdown(answer)

        # =========================
        # FEEDBACK SYSTEM
        # =========================
        col1, col2 = st.columns(2)

        with col1:
            if st.button("👍 Helpful"):
                save_feedback(answer, "positive")
                st.success("Feedback saved")

        with col2:
            if st.button("👎 Not Helpful"):
                save_feedback(answer, "negative")
                st.warning("Feedback saved")
