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
DB_FILE = "studyforge.db"


# =====================
# STYLE (FIXED SPACING)
# =====================

st.markdown("""
<style>
.user-box, .ai-box {
    padding: 14px 16px;
    border-radius: 12px;
    margin: 12px 0;
    white-space: pre-wrap;
    line-height: 1.7;
    font-size: 15px;
}

.user-box {
    background: rgba(70,120,255,0.18);
}

.ai-box {
    background: rgba(140,140,140,0.18);
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

cursor.execute("""CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY, name TEXT)""")
cursor.execute("""CREATE TABLE IF NOT EXISTS chats(id TEXT PRIMARY KEY, user_id TEXT, title TEXT, created TEXT)""")
cursor.execute("""CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id TEXT, role TEXT, content TEXT)""")
db.commit()


# =====================
# USER INIT
# =====================

if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

    cursor.execute("INSERT INTO users VALUES (?,?)",
                   (st.session_state.user_id, "User"))
    db.commit()


# =====================
# CHAT FUNCTIONS
# =====================

def create_chat():
    cid = str(uuid.uuid4())

    cursor.execute("INSERT INTO chats VALUES (?,?,?,?)",
                   (cid, st.session_state.user_id, "New Chat", str(datetime.now())))
    db.commit()
    return cid


def get_chats():
    cursor.execute("SELECT id,title FROM chats WHERE user_id=? ORDER BY created DESC",
                   (st.session_state.user_id,))
    return cursor.fetchall()


def save_message(chat, role, text):
    cursor.execute("INSERT INTO messages(chat_id,role,content) VALUES (?,?,?)",
                   (chat, role, text))
    db.commit()


def get_messages(chat):
    cursor.execute("SELECT role,content FROM messages WHERE chat_id=? ORDER BY id",
                   (chat,))
    return cursor.fetchall()


def delete_chat(chat):
    cursor.execute("DELETE FROM chats WHERE id=?", (chat,))
    cursor.execute("DELETE FROM messages WHERE chat_id=?", (chat,))
    db.commit()


# =====================
# SUBJECT DETECTION (simple but stable)
# =====================

def detect_subject(q):
    q = q.lower()

    if any(x in q for x in ["math","algebra","calculus","equation"]):
        return "Math"
    if any(x in q for x in ["force","energy","physics"]):
        return "Physics"
    if any(x in q for x in ["atom","reaction","chem"]):
        return "Chemistry"
    if any(x in q for x in ["code","python","algorithm"]):
        return "CS"
    if any(x in q for x in ["essay","grammar"]):
        return "English"

    return "General"


# =====================
# AI PROMPT (tutor behavior fixed)
# =====================

def prompt(subject):
    return f"""
You are StudyForge AI Tutor.

Subject: {subject}

You must behave like a strict but clear teacher.

Format:
1. Answer (short)
2. Explanation (bullet points, spaced)
3. Steps
4. Example
5. Key rule

Rules:
- No unnecessary questions
- Always structured
- Simple language
- Use LaTeX if needed
"""


def ask_ai(chat_id, question, subject):

    history = get_messages(chat_id)

    messages = [{"role": "system", "content": prompt(subject)}]

    for r, c in history:
        messages.append({"role": r, "content": c})

    messages.append({"role": "user", "content": question})

    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.3
    )

    return res.choices[0].message.content


# =====================
# SESSION CHAT
# =====================

if "chat_id" not in st.session_state:
    chats = get_chats()
    st.session_state.chat_id = chats[0][0] if chats else create_chat()


# =====================
# SIDEBAR
# =====================

with st.sidebar:

    st.title("⚒️ StudyForge")
    st.caption(f"{VERSION} | {CREATOR}")

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

    st.markdown(f"""
    <div class="{box}">
    {msg}
    </div>
    """, unsafe_allow_html=True)


# =====================
# INPUT
# =====================

q = st.chat_input("Ask anything...")

if q:

    save_message(st.session_state.chat_id, "user", q)

    subject = detect_subject(q)

    ans = ask_ai(st.session_state.chat_id, q, subject)

    save_message(st.session_state.chat_id, "assistant", ans)

    st.rerun()


# =====================
# ADMIN (FIXED / SAFE)
# =====================

if "admin" not in st.session_state:
    st.session_state.admin = False


st.sidebar.divider()
st.sidebar.subheader("Admin Console")

cmd = st.sidebar.text_input("Command (/login, /stats, /db)")

if cmd:

    parts = cmd.split(" ")
    action = parts[0]

    if action == "/login" and len(parts) > 1:
        if st.secrets.get("ADMIN_PASSWORD","") == parts[1]:
            st.session_state.admin = True
            st.sidebar.success("Admin logged in")
        else:
            st.sidebar.error("Wrong password")

    elif action == "/logout":
        st.session_state.admin = False
        st.sidebar.info("Logged out")

    elif action == "/stats" and st.session_state.admin:
        st.sidebar.write("Users:", cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0])
        st.sidebar.write("Chats:", cursor.execute("SELECT COUNT(*) FROM chats").fetchone()[0])
        st.sidebar.write("Messages:", cursor.execute("SELECT COUNT(*) FROM messages").fetchone()[0])

    elif action == "/db" and st.session_state.admin:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "rb") as f:
                st.sidebar.download_button("Download DB", f.read(), file_name=DB_FILE)
