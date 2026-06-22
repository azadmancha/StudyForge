import streamlit as st
import sqlite3
from groq import Groq


# =====================
# CONFIG
# =====================

st.set_page_config(
    page_title="StudyForge AI",
    page_icon="⚒️",
    layout="wide"
)


# =====================
# UI CSS
# =====================

st.markdown("""
<style>

.user-box {
    background-color: rgba(70,120,255,0.18);
    padding: 14px;
    border-radius: 14px;
    margin: 10px 0;
    border: 1px solid rgba(100,100,100,0.25);
}


.ai-box {
    background-color: rgba(140,140,140,0.15);
    padding: 14px;
    border-radius: 14px;
    margin: 10px 0;
    border: 1px solid rgba(100,100,100,0.25);
}


/* Fix chat input red issue */
textarea {
    background-color: transparent !important;
}


.stChatInputContainer {
    border-color: rgba(120,120,120,0.3) !important;
}


.subject-box {
    padding: 10px;
    border-radius: 12px;
    background-color: rgba(120,120,120,0.12);
    margin-bottom:10px;
}

</style>
""", unsafe_allow_html=True)



# =====================
# GROQ
# =====================

if "GROQ_API_KEY" not in st.secrets:

    st.error(
        "Missing GROQ_API_KEY in Streamlit Secrets"
    )

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
        (role,content)
    )

    db.commit()



def get_messages():

    cursor.execute(
        "SELECT role,content FROM messages ORDER BY id"
    )

    return cursor.fetchall()



def save_feedback(text, rating):

    cursor.execute(
        "INSERT INTO feedback(response,rating) VALUES (?,?)",
        (text,rating)
    )

    db.commit()



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


def detect_subject(question):

    q = question.lower()


    keywords = {

        "Mathematics":
        ["math","equation","algebra","calculus","geometry",
         "trigonometry","integral","probability"],


        "Physics":
        ["force","energy","motion","velocity",
         "acceleration","wave","electric"],


        "Chemistry":
        ["atom","molecule","reaction",
         "chemical","bond","acid"],


        "Biology":
        ["cell","dna","gene","biology",
         "plant","body"],


        "Computer Science":
        ["code","python","algorithm",
         "program","database"],


        "English":
        ["grammar","essay","writing",
         "literature"],


        "History":
        ["war","empire","revolution"],


        "Geography":
        ["earth","map","climate"],


        "Economics":
        ["market","demand","supply"],


        "Social Science":
        ["government","society","civics"]

    }


    scores = {}

    for subject, words in keywords.items():

        scores[subject] = sum(
            1 for word in words if word in q
        )


    best = max(scores, key=scores.get)


    if scores[best] == 0:
        return "General"


    return best



# =====================
# AI
# =====================

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

Rules:
- Teach step by step
- Explain concepts
- Adjust difficulty
- Be accurate

Question:
{question}

"""



def ask_ai(prompt):

    try:

        result = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[
                {
                    "role":"user",
                    "content":prompt
                }
            ],

            temperature=0.4
        )

        return result.choices[0].message.content


    except Exception:

        return "AI failed. Check Groq settings."



# =====================
# SIDEBAR
# =====================

with st.sidebar:

    st.title("⚒️ StudyForge")


    difficulty = st.selectbox(
        "Difficulty",
        ["Easy","Normal","Advanced"]
    )


    mode = st.selectbox(
        "Mode",
        ["Normal","Exam","Hint"]
    )


    if st.button("Clear Chat"):

        cursor.execute(
            "DELETE FROM messages"
        )

        db.commit()

        st.rerun()



# =====================
# MAIN
# =====================

st.title("⚒️ StudyForge AI")

st.caption(
    "Adaptive AI learning assistant"
)


st.subheader("Available Subjects")

st.markdown(
    " • ".join(SUBJECTS)
)



for role, message in get_messages():

    box = "user-box" if role=="user" else "ai-box"

    st.markdown(
        f"""
        <div class="{box}">
        {message}
        </div>
        """,
        unsafe_allow_html=True
    )



question = st.chat_input(
    "Ask your question..."
)



if question:

    save_message(
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
            create_prompt(
                question,
                subject,
                difficulty,
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
        "assistant",
        answer
    )


    c1,c2 = st.columns(2)


    with c1:

        if st.button("👍 Helpful"):

            save_feedback(answer,"positive")
            st.success("Saved")


    with c2:

        if st.button("👎 Improve"):

            save_feedback(answer,"negative")
            st.warning("Saved")
