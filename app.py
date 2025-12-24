import streamlit as st
from main import RAGPipeline

# הגדרות דף
st.set_page_config(page_title="AI Resume Analyzer", page_icon="🔍", layout="centered")

# עיצוב כותרת
st.title("🔍 AI Resume Analysis Tool")
st.markdown("שאל שאלות על קורות החיים שנמצאים בתיקיית ה-Data שלך")

# אתחול ה-Pipeline בזיכרון של האתר (Session State)
if "pipeline" not in st.session_state:
    st.session_state.pipeline = None
    with st.spinner("מאתחל את המנוע... זה קורה רק פעם אחת"):
        try:
            pipeline = RAGPipeline()
            # טעינת אינדקס או יצירה
            if not pipeline.load_index():
                docs = pipeline.load_pdfs()
                if docs:
                    chunks = pipeline.chunk_documents(docs)
                    pipeline.create_and_save_index(chunks)
                else:
                    st.warning("לא נמצאו קבצי PDF בתיקיית data. אנא הוסף קבצי PDF כדי להמשיך.")
            st.session_state.pipeline = pipeline
            st.success("המערכת מוכנה!")
        except Exception as e:
            import traceback
            st.error(f"שגיאה באתחול: {e}")
            st.code(traceback.format_exc())
            st.session_state.pipeline = None

# ניהול היסטוריית הצ'אט
if "messages" not in st.session_state:
    st.session_state.messages = []

# הצגת הודעות קודמות מהשיחה
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# תיבת קלט מהמשתמש (Chat Input)
if prompt := st.chat_input("למשל: מה החוזקות של המועמדים?"):
    # הוספת הודעת המשתמש למסך ולזיכרון
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # יצירת תשובה מה-AI
    if "pipeline" in st.session_state and st.session_state.pipeline is not None:
        with st.chat_message("assistant"):
            with st.spinner("ה-AI סורק את המסמכים..."):
                try:
                    # שימוש בפונקציה ask_question שכבר כתבנו
                    response = st.session_state.pipeline.ask_question(prompt)
                    st.markdown(response)
                    # שמירת התשובה בזיכרון השיחה
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"קרתה שגיאה בזמן החיפוש: {e}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
    else:
        with st.chat_message("assistant"):
            error_msg = "שגיאה: המערכת לא אותחלה כראוי. אנא רענן את הדף או בדוק את לוגי השגיאות."
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})