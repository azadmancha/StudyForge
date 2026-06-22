import streamlit as st
import sqlite3
from groq import Groq


# -----------------------
# APP CONFIG
# -----------------------

st.set_page_config(
    page_title="StudyForge AI",
    page_icon="⚒️",
    layout="wide"
)


st.markdown("""
<style>

.user-box {
    background:#dbeafe;
    padding:14px;
    border-radius:16px;
    margin:12px 0;
}

.ai-box {
    background:#f3f4f6;
    padding:14px;
    border-radius:16px;
    margin:12px 0;
}

</style>
""", unsafe_allow_html=True)



# -----------------------
# GROQ SETUP
# -----------------------

if "GROQ_API_KEY" not in st.secrets:

    st.error(
        "Missing GROQ_API_KEY in Streamlit Secrets"
    )

    st.stop()


client = Groq(
    api_key=st.secrets["GROQ_API_KEY"]
)



# -----------------------
# DATABASE
# -----------------------

db = sqlite3.connect(
    "studyforge.db",
    check_same_thread=False
)

cursor = db.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS messages(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT NOT NULL,
    content TEXT NOT NULL
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
        """
        INSERT INTO messages(role,content)
        VALUES (?,?)
        """,
        (role, content)
    )

    db.commit()



def get_messages():

    cursor.execute(
        """
        SELECT role,content
        FROM messages
        ORDER BY id
        """
    )

    return cursor.fetchall()



def save_feedback(response, rating):

    cursor.execute(
        """
        INSERT INTO feedback(response,rating)
        VALUES (?,?)
        """,
        (response, rating)
    )

    db.commit()



# -----------------------
# SUBJECT DETECTION
# -----------------------

def detect_subject(question):

    q = question.lower()


    subject_keywords = {

        "Mathematics": [
            "math","equation","algebra",
            "calculus","geometry",
            "trigonometry","integral",
            "derivative","probability",
            "statistics"
        ],

        "Physics": [
            "force","motion",
            "velocity","acceleration",
            "energy","wave",
            "electricity","physics"
        ],

        "Chemistry": [
            "atom","molecule",
            "reaction","chemical",
            "bond","acid",
            "periodic table"
        ],

        "Biology": [
            "cell","dna",
            "gene","organ",
            "plant","biology"
        ],

        "Computer Science": [
            "python","code",
            "program","algorithm",
            "database","computer"
        ],

        "English": [
            "grammar",
            "essay",
            "writing",
            "literature"
        ],

        "History": [
            "war",
            "empire",
            "revolution",
            "history"
        ],

        "Geography": [
            "climate",
            "earth",
            "map",
            "geography"
        ],

        "Economics": [
            "market",
            "demand",
            "supply",
            "economy"
        ],

        "Social Science": [
            "government",
            "society",
            "civics"
        ]

    }


    scores = {}


    for subject, words in subject_keywords.items():

        scores[subject] = sum(
            1 for word in words if word in q
        )


    best = max(
        scores,
        key=scores.get
    )


    if scores[best] == 0:
        return "General"


    return best



# -----------------------
# PROMPT SYSTEM
# -----------------------

def create_prompt(
    question,
    subject,
    difficulty,
    mode
):

    extra = ""

    if mode == "Exam":
        extra = "Answer in exam style with proper steps."

    elif mode == "Hint":
        extra = "Give hints first and avoid revealing full solution immediately."


    return f"""

You are StudyForge AI Tutor.

Subject: {subject}

Difficulty: {difficulty}

{extra}

Rules:
- Teach clearly
- Explain step by step
- Be accurate
- Adjust explanation level
- Do not skip reasoning

Question:
{question}

"""



# -----------------------
# AI RESPONSE
# -----------------------

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

            temperature=0.4
        )

        return response.choices[0].message.content


    except Exception as e:

        return (
            "AI error occurred. "
            "Please check your Groq key/model settings."
        )



# -----------------------
# SIDEBAR
# -----------------------

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


    if st.button("Clear Chat"):

        cursor.execute(
            "DELETE FROM messages"
        )

        db.commit()

        st.rerun()



# -----------------------
# MAIN
# -----------------------

st.title("⚒️ StudyForge AI")

st.caption(
    "Adaptive AI learning assistant"
)



for role, message in get_messages():

    css = (
        "user-box"
        if role == "user"
        else "ai-box"
    )

    st.markdown(
        f"""
        <div class="{css}">
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


    col1, col2 = st.columns(2)


    with col1:

        if st.button(
            "👍 Helpful",
            key="helpful_" + question[:10]
        ):

            save_feedback(
                answer,
                "positive"
            )

            st.success("Saved")


    with col2:

        if st.button(
            "👎 Improve",
            key="improve_" + question[:10]
        ):

            save_feedback(
                answer,
                "negative"
            )

            st.warning("Saved")
