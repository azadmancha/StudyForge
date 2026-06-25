import streamlit as st
import sqlite3
from groq import Groq
import uuid
from datetime import datetime
import os


# =====================
# CONFIG
# =====================

st.set_page_config(
    page_title="StudyForge AI",
    page_icon="⚒️",
    layout="wide"
)

VERSION = "v1.8"
CREATOR = "Azad"
DB_FILE = "studyforge_v18.db"


# =====================
# STYLE
# =====================

st.markdown("""
<style>
.user-box {
    background: rgba(70,120,255,0.18);
    padding:14px;
    border-radius:14px;
    margin:10px 0;
}

.ai-box {
    background: rgba(140,140,140,0.18);
    padding:14px;
    border-radius:14px;
    margin:10px 0;
}
</style>
""", unsafe_allow_html=True)


# =====================
# GROQ
# =====================

if "GROQ_API_KEY" not in st.secrets:
    st.error("Missing GROQ_API_KEY")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])


# =====================
# DATABASE
# =====================

db = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
id TEXT PRIMARY KEY,
name TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS chats(
id TEXT PRIMARY KEY,
user_id TEXT,
title TEXT,
created TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS messages(
id INTEGER PRIMARY KEY AUTOINCREMENT,
chat_id TEXT,
role TEXT,
content TEXT
)
""")

db.commit()


# =====================
# USER INIT
# =====================

if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

    cursor.execute(
        "INSERT INTO users VALUES (?,?)",
        (st.session_state.user_id, "Student")
    )
    db.commit()


# =====================
# CHAT FUNCTIONS
# =====================

def create_chat(title="New Chat"):
    cid = str(uuid.uuid4())

    cursor.execute("""
        INSERT INTO chats VALUES (?,?,?,?)
    """, (
        cid,
        st.session_state.user_id,
        title,
        str(datetime.now())
    ))

    db.commit()
    return cid


def get_chats():
    cursor.execute("""
        SELECT id,title FROM chats
        WHERE user_id=?
        ORDER BY created DESC
    """, (st.session_state.user_id,))

    return cursor.fetchall()


def update_title(chat_id, title):
    cursor.execute("""
        UPDATE chats SET title=?
        WHERE id=?
    """, (title, chat_id))
    db.commit()


def save_message(chat, role, text):
    cursor.execute("""
        INSERT INTO messages(chat_id,role,content)
        VALUES (?,?,?)
    """, (chat, role, text))
    db.commit()


def get_messages(chat):
    cursor.execute("""
        SELECT role,content FROM messages
        WHERE chat_id=?
        ORDER BY id
    """, (chat,))
    return cursor.fetchall()


def delete_chat(chat):
    cursor.execute("DELETE FROM chats WHERE id=?", (chat,))
    cursor.execute("DELETE FROM messages WHERE chat_id=?", (chat,))
    db.commit()


# =====================
# SUBJECT DETECTION
# =====================

def detect_subject(q):
    q = q.lower()

    data = {
        "Math": ["math","algebra","equation","geometry"],
        "Physics": ["force","energy","motion","velocity"],
        "Chemistry": ["atom","reaction","chemical"],
        "CS": ["code","python","algorithm","api"],
        "English": ["essay","grammar","writing"],
        "History": ["war","empire","history"]
    }

    scores = {}

    for s, words in data.items():
        scores[s] = sum(w in q for w in words)

    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "General"


# =====================
# SYSTEM PROMPT (TUTOR)
# =====================

def system_prompt(subject):
    return f"""
You are StudyForge AI, a personal tutor created by Azad.

Subject: {subject}

You are NOT a chatbot. You are a structured tutor.

RULES:
- Teach step by step
- Start simple, then deepen
- Use examples only when useful
- Adapt to student level
- Use chat history for context
- Never restart explanations unnecessarily

OUTPUT FORMAT:
1. Direct answer
2. Explanation
3. Example (if needed)
4. Summary
"""


# =====================
# AI CALL (FIXED MEMORY)
# =====================

def ask_ai(chat_id, question, subject):

    try:
        history = get_messages(chat_id)

        messages = [
            {
                "role": "system",
                "content": system_prompt(subject)
            }
        ]

        for role, content in history:
            messages.append({
                "role": role,
                "content": content
            })

        messages.append({
            "role": "user",
            "content": question
        })

        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.3
        )

        return res.choices[0].message.content

    except:
        return "AI error."


# =====================
# SESSION CHAT
# =====================

if "chat_id" not in st.session_state:
    chats = get_chats()
    st.session_state.chat_id = chats[0][0] if chats else create_chat()


# =====================
# CHAT TITLE
# =====================

def make_title(text):
    return text[:45] + "..." if len(text) > 45 else text


# =====================
# SIDEBAR
# =====================

with st.sidebar:

    st.title("⚒️ StudyForge")
    st.caption(f"{VERSION} | Created by {CREATOR}")

    if st.button("➕ New Chat"):
        st.session_state.chat_id = create_chat()
        st.rerun()

    st.divider()

    st.subheader("Chats")

    for cid, title in get_chats():
        if st.button(title, key=cid):
            st.session_state.chat_id = cid
            st.rerun()

    if st.button("🗑 Delete Chat"):
        delete_chat(st.session_state.chat_id)
        st.session_state.chat_id = create_chat()
        st.rerun()


# =====================
# MAIN UI
# =====================

st.title("⚒️ StudyForge AI")

for role, msg in get_messages(st.session_state.chat_id):

    box = "user-box" if role == "user" else "ai-box"

    st.markdown(f"<div class='{box}'>{msg}</div>", unsafe_allow_html=True)


question = st.chat_input("Ask anything...")

if question:

    save_message(st.session_state.chat_id, "user", question)

    subject = detect_subject(question)

    answer = ask_ai(st.session_state.chat_id, question, subject)

    save_message(st.session_state.chat_id, "assistant", answer)

    # auto rename chat
    chats = get_chats()
    for cid, title in chats:
        if cid == st.session_state.chat_id and title == "New Chat":
            update_title(cid, make_title(question))

    st.rerun()


# =====================
# ADMIN (/admin password)
# =====================

admin_input = st.text_input("")

if admin_input.startswith("/admin"):

    try:
        password = admin_input.split(" ", 1)[1]
    except:
        password = ""

    if password == st.secrets.get("ADMIN_PASSWORD", ""):

        st.success("Admin Access Granted")

        st.subheader("📊 Dashboard")

        st.write("Users:", cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0])
        st.write("Chats:", cursor.execute("SELECT COUNT(*) FROM chats").fetchone()[0])
        st.write("Messages:", cursor.execute("SELECT COUNT(*) FROM messages").fetchone()[0])

        if os.path.exists(DB_FILE):
            with open(DB_FILE, "rb") as f:
                db_bytes = f.read()

            st.download_button(
                "Download DB",
                db_bytes,
                file_name=DB_FILE,
                mime="application/octet-stream"
            )

    elif password:
        st.error("Invalid password")
