import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import streamlit as st
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our modules
from src.ocr import extract_text_from_image_bytes
from src.text_extractor import extract_text_from_pdf_bytes
from src.summarizer import summarize_text
from src.qa import answer_question
from src.quiz import generate_quiz

API_KEY = os.getenv("GROQ_API_KEY", "").strip()

st.set_page_config(
    page_title="Study Assistant",
    page_icon="◆",
    layout="wide",
)

st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}

    html, body, [class*="css"] {
        background-color: #121212;
        color: #E4E4E4;
        font-family: -apple-system, "Segoe UI", Inter, sans-serif;
    }
    .stApp {
        background-color: #121212;
    }
    [data-testid="stSidebar"] {
        background-color: #171717;
        border-right: 1px solid #262626;
    }

    .title {
        font-size: 1.6rem;
        font-weight: 600;
        color: #F2F2F2;
        margin-bottom: 0;
        letter-spacing: -0.3px;
    }
    .subtitle {
        color: #8A8A8A;
        font-size: 0.92rem;
        margin-top: 0.15rem;
        margin-bottom: 1.6rem;
    }

    .box {
        background-color: #1A1A1A;
        border: 1px solid #2A2A2A;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin: 0.8rem 0;
        line-height: 1.6;
        color: #DCDCDC;
    }
    .quiz-q {
        background-color: #1A1A1A;
        border: 1px solid #2A2A2A;
        border-left: 3px solid #4A4A4A;
        border-radius: 8px;
        padding: 0.8rem 1rem;
        margin: 0.7rem 0 0.3rem 0;
    }

    .stButton > button {
        background-color: #262626;
        color: #F0F0F0;
        border: 1px solid #333;
        border-radius: 8px;
        font-weight: 500;
    }
    .stButton > button:hover {
        background-color: #333;
        border-color: #444;
        color: #fff;
    }

    [data-testid="stFileUploader"] {
        background-color: #171717;
        border-radius: 8px;
    }

    hr { border-color: #262626; }
</style>
""", unsafe_allow_html=True)


# Header 
st.markdown('<div class="title">Study Assistant</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Upload your notes and get a summary, ask questions, or test yourself with a quiz.</div>',
    unsafe_allow_html=True,
)

# Sidebar 
with st.sidebar:
    st.markdown("**Upload material**")
    uploaded_file = st.file_uploader(
        "File",
        type=["txt", "pdf", "png", "jpg", "jpeg"],
        label_visibility="collapsed",
    )

    st.write("")
    st.markdown("**Mode**")
    operation = st.radio(
        "Mode",
        options=["Summarize", "Ask a Question", "Generate Quiz"],
        index=0,
        label_visibility="collapsed",
    )

    if not API_KEY:
        st.write("")
        st.caption("⚠ No GROQ_API_KEY found in .env")

# Main Content 

if "extracted_text" not in st.session_state:
    st.session_state.extracted_text = ""
if "last_uploaded_file" not in st.session_state:
    st.session_state.last_uploaded_file = None

if uploaded_file is not None:
    file_type = uploaded_file.name.split(".")[-1].lower()
    if (
        st.session_state.last_uploaded_file != uploaded_file.name
        or not st.session_state.extracted_text
    ):
        st.session_state.last_uploaded_file = uploaded_file.name
        with st.spinner("Extracting text..."):
            try:
                if file_type == "txt":
                    st.session_state.extracted_text = uploaded_file.read().decode("utf-8", errors="ignore").strip()
                elif file_type == "pdf":
                    pdf_bytes = BytesIO(uploaded_file.read())
                    st.session_state.extracted_text = extract_text_from_pdf_bytes(pdf_bytes)
                elif file_type in ["png", "jpg", "jpeg"]:
                    image_bytes = uploaded_file.getvalue()
                    st.session_state.extracted_text = extract_text_from_image_bytes(image_bytes)
            except Exception as e:
                st.error(f"Couldn't read that file: {e}")
                st.session_state.extracted_text = ""

    st.markdown(f"**{uploaded_file.name}**")

    if file_type in ["png", "jpg", "jpeg"]:
        st.image(uploaded_file, use_container_width=True)

    text = st.session_state.extracted_text

    if text:
        with st.expander("View extracted text"):
            st.text_area("Extracted", value=text, height=180, disabled=True, label_visibility="collapsed")

        st.markdown("---")

        # Summarize
        if operation == "Summarize":
            if st.button("Generate summary", type="primary"):
                if not API_KEY:
                    st.error("No API key configured. Add GROQ_API_KEY to your .env file.")
                else:
                    with st.spinner("Summarizing..."):
                        try:
                            summary = summarize_text(text, api_key=API_KEY)
                            st.markdown(f'<div class="box">{summary}</div>', unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"Summarization failed: {e}")

        # Q&A
        elif operation == "Ask a Question":
            question = st.text_input(
                "Question",
                placeholder="Ask something about your notes...",
                label_visibility="collapsed",
            )
            if st.button("Get answer", type="primary"):
                if not API_KEY:
                    st.error("No API key configured. Add GROQ_API_KEY to your .env file.")
                elif not question.strip():
                    st.warning("Type a question first.")
                else:
                    with st.spinner("Thinking..."):
                        try:
                            answer = answer_question(text, question, api_key=API_KEY)
                            st.markdown(f'<div class="box">{answer}</div>', unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"Couldn't get an answer: {e}")

        # Quiz
        elif operation == "Generate Quiz":
            col_q, col_btn = st.columns([2, 1])
            with col_q:
                num_q = st.slider("Questions", min_value=3, max_value=10, value=5, label_visibility="collapsed")
            with col_btn:
                gen_clicked = st.button("Generate quiz", type="primary")

            if gen_clicked:
                if not API_KEY:
                    st.error("No API key configured. Add GROQ_API_KEY to your .env file.")
                else:
                    with st.spinner("Building quiz..."):
                        try:
                            quiz = generate_quiz(text, num_questions=num_q, api_key=API_KEY)
                            st.session_state.quiz = quiz
                            st.session_state.submitted = False
                        except Exception as e:
                            st.error(f"Quiz generation failed: {e}")

            if "quiz" in st.session_state and st.session_state.quiz:
                quiz = st.session_state.quiz
                user_answers = {}

                st.markdown("---")

                with st.form("quiz_form"):
                    for i, q in enumerate(quiz, 1):
                        st.markdown(
                            f'<div class="quiz-q"><strong>{i}.</strong> {q["question"]}</div>',
                            unsafe_allow_html=True,
                        )
                        user_answers[i] = st.radio(
                            f"Options for Q{i}:",
                            options=q["options"],
                            key=f"quiz_opt_{i}",
                            label_visibility="collapsed",
                        )

                    submitted = st.form_submit_button("Submit", type="primary")
                    if submitted:
                        st.session_state.submitted = True

                if st.session_state.get("submitted", False):
                    st.markdown("---")
                    score = 0
                    for i, q in enumerate(quiz, 1):
                        user_ans = user_answers.get(i)
                        correct_ans = q["answer"]
                        is_correct = user_ans and (
                            user_ans.strip() == correct_ans.strip()
                            or user_ans.strip().startswith(correct_ans[:2])
                        )
                        if is_correct:
                            score += 1
                            st.success(f"{i}. Correct — {user_ans}")
                        else:
                            st.error(f"{i}. Incorrect — you picked {user_ans} · correct: {correct_ans}")

                    st.metric("Score", f"{score} / {len(quiz)}", f"{int((score/len(quiz))*100)}%")
    else:
        st.warning("Couldn't find any readable text in this file — try another one.")

else:
    st.write("")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Summarize**")
        st.caption("Turn long notes into a short, clear summary.")
    with col2:
        st.markdown("**Ask questions**")
        st.caption("Get answers grounded in what you uploaded.")
    with col3:
        st.markdown("**Quiz yourself**")
        st.caption("Auto-generated questions to check what stuck.")

    st.write("")
    st.caption("Upload a text file, PDF, or image from the sidebar to get started.")