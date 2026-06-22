import streamlit as st
import sqlite3
from groq import Groq
import uuid


# =====================
# CONFIG
# =====================

st.set_page_config(
    page_title="StudyForge AI",
    page_icon="⚒️",
    layout="wide"
)


st.markdown("""
<style>

.user-box {
    background: rgba(70,120,255,0.18);
    padding:14px;
    border-radius:14px;
    margin:10px 0;
    border:1px solid rgba(120,120,120,0.25);
}

.ai-box {
    background: rgba(140,140,140,0.18);
    padding:14px;
    border-radius:14px;
    margin:10px 0;
    border:1px solid rgba(120,120,120,0.25);
}

textarea {
    background: transparent !important;
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
# DATABASE
# =====================

db = sqlite3.connect(
    "studyforge.db",
    check_same_thread=False
)

cursor = db.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS chats(
id TEXT PRIMARY KEY,
title TEXT
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


cursor.execute("""
CREATE TABLE IF NOT EXISTS feedback(
id INTEGER PRIMARY KEY AUTOINCREMENT,
response TEXT,
rating TEXT
)
""")


db.commit()



def create_chat():

    cid = str(uuid.uuid4())

    cursor.execute(
        "INSERT INTO chats VALUES (?,?)",
        (cid,"New Chat")
    )

    db.commit()

    return cid



def get_chats():

    cursor.execute(
        "SELECT * FROM chats ORDER BY rowid DESC"
    )

    return cursor.fetchall()



def save_message(chat,role,text):

    cursor.execute(
        """
        INSERT INTO messages
        (chat_id,role,content)
        VALUES (?,?,?)
        """,
        (chat,role,text)
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



def save_feedback(text,rating):

    cursor.execute(
        """
        INSERT INTO feedback(response,rating)
        VALUES (?,?)
        """,
        (text,rating)
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
    ["math","equation","algebra","calculus",
     "geometry","probability"],

    "Physics":
    ["force","energy","motion",
     "velocity","physics"],

    "Chemistry":
    ["atom","reaction",
     "chemical","chemistry"],

    "Biology":
    ["cell","dna","biology"],

    "Computer Science":
    ["code","python",
     "algorithm","program"],

    "English":
    ["grammar","essay",
     "writing"],

    "History":
    ["war","empire",
     "history"],

    "Geography":
    ["earth","climate",
     "map"],

    "Economics":
    ["market","demand",
     "supply"],

    "Social Science":
    ["government",
     "society"]

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

Subject:
{subject}

Learning depth:
{depth}

Mode:
{mode}

Rules:
- Answer the question directly first.
- Do not ask "can you confirm?"
- Do not ask for unnecessary validation.
- Match length to difficulty.
- Simple calculations need short answers.
- Teach step by step for learning questions.
- Use examples only when useful.
- Be accurate.

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


    if st.button("➕ New Chat"):

        st.session_state.chat_id = create_chat()

        st.rerun()



    st.divider()


    st.subheader("Chats")


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

        st.session_state.chat_id = create_chat()

        st.rerun()



# =====================
# MAIN
# =====================

st.title("⚒️ StudyForge AI")


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


    st.markdown(
        f"""
        <div class="user-box">
        {question}
        </div>
        """,
        unsafe_allow_html=True
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


    st.markdown(
        f"""
        <div class="ai-box">
        {answer}
        </div>
        """,
        unsafe_allow_html=True
    )


    save_message(
        st.session_state.chat_id,
        "assistant",
        answer
        )
