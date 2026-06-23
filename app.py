import streamlit as st
import sqlite3
from groq import Groq
import uuid
from datetime import datetime


# =====================
# CONFIG
# =====================

st.set_page_config(
    page_title="StudyForge AI",
    page_icon="⚒️",
    layout="wide"
)

VERSION = "v1.7"
CREATOR = "Azad"


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
    st.error("Missing GROQ_API_KEY in Streamlit Secrets")
    st.stop()


client = Groq(
    api_key=st.secrets["GROQ_API_KEY"]
)


# =====================
# DATABASE v1.7
# =====================

db = sqlite3.connect(
    "studyforge_v17.db",
    check_same_thread=False
)

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
# USER
# =====================

if "user_id" not in st.session_state:

    st.session_state.user_id = str(uuid.uuid4())

    cursor.execute(
        """
        INSERT INTO users
        VALUES (?,?)
        """,
        (
            st.session_state.user_id,
            "User"
        )
    )

    db.commit()



# =====================
# CHAT FUNCTIONS
# =====================

def create_chat():

    cid = str(uuid.uuid4())

    cursor.execute(
        """
        INSERT INTO chats
        VALUES (?,?,?,?)
        """,
        (
            cid,
            st.session_state.user_id,
            "New Chat",
            str(datetime.now())
        )
    )

    db.commit()

    return cid



def get_chats():

    cursor.execute(
        """
        SELECT id,title
        FROM chats
        WHERE user_id=?
        ORDER BY created DESC
        """,
        (st.session_state.user_id,)
    )

    return cursor.fetchall()



def save_message(chat, role, text):

    cursor.execute(
        """
        INSERT INTO messages
        (chat_id,role,content)
        VALUES (?,?,?)
        """,
        (
            chat,
            role,
            text
        )
    )

    db.commit()



def get_messages(chat):

    cursor.execute(
        """
        SELECT role,content
        FROM messages
        WHERE chat_id=?
        ORDER BY id
        """,
        (chat,)
    )

    return cursor.fetchall()



def delete_chat(chat):

    cursor.execute(
        "DELETE FROM chats WHERE id=?",
        (chat,)
    )

    cursor.execute(
        "DELETE FROM messages WHERE chat_id=?",
        (chat,)
    )

    db.commit()



# =====================
# SESSION
# =====================

if "chat_id" not in st.session_state:

    chats = get_chats()

    if chats:
        st.session_state.chat_id = chats[0][0]

    else:
        st.session_state.chat_id = create_chat()

# =====================
# SUBJECTS
# =====================

SUBJECTS = [
"Mathematics",
"Physics",
"Chemistry",
"Biology",
"Computer Science",
"English",
"History",
"Geography",
"Economics",
"Social Science",
"General"
]


def detect_subject(q):

    q = q.lower()


    data = {

    "Mathematics":
    [
    "math",
    "equation",
    "algebra",
    "calculus",
    "geometry",
    "probability",
    "trigonometry",
    "statistics"
    ],


    "Physics":
    [
    "force",
    "energy",
    "motion",
    "velocity",
    "acceleration",
    "physics",
    "electricity",
    "wave"
    ],


    "Chemistry":
    [
    "atom",
    "reaction",
    "chemical",
    "chemistry",
    "molecule",
    "bond"
    ],


    "Biology":
    [
    "cell",
    "dna",
    "biology",
    "organ",
    "genetics"
    ],


    "Computer Science":
    [
    "code",
    "python",
    "program",
    "algorithm",
    "database",
    "api",
    "computer"
    ],


    "English":
    [
    "grammar",
    "essay",
    "writing",
    "literature",
    "vocabulary"
    ],


    "History":
    [
    "war",
    "empire",
    "history",
    "civilization",
    "revolution"
    ],


    "Geography":
    [
    "earth",
    "climate",
    "map",
    "geography",
    "environment"
    ],


    "Economics":
    [
    "market",
    "demand",
    "supply",
    "economics",
    "inflation"
    ],


    "Social Science":
    [
    "government",
    "society",
    "politics",
    "culture"
    ]

    }


    scores = {}

    for subject,words in data.items():

        scores[subject] = sum(
            word in q for word in words
        )


    best = max(
        scores,
        key=scores.get
    )


    if scores[best] == 0:
        return "General"


    return best



# =====================
# AI
# =====================


def build_prompt(
    question,
    subject,
    depth,
    mode
):

    return f"""

You are StudyForge AI Tutor.

You were created by Azad.

Never say you were created by Meta,
OpenAI, or any other company.

Subject:
{subject}

Learning depth:
{depth}

Mode:
{mode}

Rules:
- Answer directly first.
- Never ask "can you confirm?"
- Do not ask unnecessary validation.
- Adjust explanation to user level.
- Simple questions get simple answers.
- Teaching questions get step-by-step explanations.

Question:
{question}

"""



def ask_ai(prompt):

    try:

        response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[
                {
                    "role":"user",
                    "content":prompt
                }
            ],

            temperature=0.3
        )


        return response.choices[0].message.content


    except Exception:

        return "AI error. Check Groq settings."



# =====================
# SIDEBAR
# =====================


with st.sidebar:

    st.title("⚒️ StudyForge")

    st.caption(
        f"{VERSION} | Created by {CREATOR}"
    )


    if st.button("➕ New Chat"):

        st.session_state.chat_id = create_chat()
        st.rerun()



    st.divider()

    st.subheader("Your Chats")


    for cid,title in get_chats():

        if st.button(
            title,
            key=cid
        ):

            st.session_state.chat_id = cid
            st.rerun()



    st.divider()


    depth = st.selectbox(
        "Learning Depth",
        [
        "Quick",
        "Balanced",
        "Deep Dive",
        "Expert"
        ]
    )


    mode = st.selectbox(
        "Mode",
        [
        "Normal",
        "Exam Prep",
        "Hint Mode",
        "Concept Builder"
        ]
    )


    if st.button("Delete Current Chat"):

        delete_chat(
            st.session_state.chat_id
        )

        st.session_state.chat_id=create_chat()

        st.rerun()



# =====================
# MAIN UI
# =====================

st.title("⚒️ StudyForge AI")

st.caption(
    f"{VERSION} — Created by {CREATOR}"
)


st.subheader("Available Subjects")

st.write(
    " • ".join(SUBJECTS)
)



for role,msg in get_messages(
    st.session_state.chat_id
):

    box = (
        "user-box"
        if role=="user"
        else "ai-box"
    )


    st.markdown(
        f"""
        <div class="{box}">
        {msg}
        </div>
        """,
        unsafe_allow_html=True
    )



question = st.chat_input(
    "Ask anything..."
)



if question:


    save_message(
        st.session_state.chat_id,
        "user",
        question
    )


    subject = detect_subject(question)


    with st.spinner("Thinking..."):


        answer = ask_ai(
            build_prompt(
                question,
                subject,
                depth,
                mode
            )
        )



    save_message(
        st.session_state.chat_id,
        "assistant",
        answer
    )


    st.rerun()
