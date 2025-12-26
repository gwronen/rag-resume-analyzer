import streamlit as st
import os
import time
import shutil
from main import RAGPipeline
from prometheus_client import start_http_server

# --- 1. אתחול שרת המטריקות (Prometheus) ---
@st.cache_resource
def start_metrics_server():
    try:
        # פתיחת פורט 8000 עבור פרומתאוס
        start_http_server(8000)
        print("📊 Metrics server running on port 8000")
    except Exception as e:
        # אם הפורט כבר פתוח (בריענון של Streamlit), נמשיך כרגיל
        pass

start_metrics_server()

# --- 2. הגדרות דף ועיצוב ---
st.set_page_config(page_title="Fetcherr Style RAG", page_icon="✈️", layout="wide")
st.title("🔍 AI Resume & Data Analyzer")
st.markdown("---")

# --- 3. לוגיקת ניהול האינדקס ---
def rebuild_system():
    """מוחק אינדקס קיים ובונה אחד חדש מכל הקבצים בתיקיית data"""
    # מחיקת תיקיית האינדקס מהדיסק
    if os.path.exists("faiss_index"):
        try:
            shutil.rmtree("faiss_index")
        except Exception as e:
            st.error(f"שגיאה במחיקת האינדקס: {e}")
    
    pipeline = RAGPipeline()
    with st.spinner("סורק את כל קבצי ה-PDF ומייצר אינדקס חדש..."):
        docs = pipeline.load_pdfs()
        if docs:
            chunks = pipeline.chunk_documents(docs)
            success = pipeline.create_and_save_index(chunks)
            if success:
                st.sidebar.success(f"האינדקס נבנה מחדש! נסרקו {len(os.listdir('./data'))} קבצים.")
                return pipeline
        else:
            st.sidebar.error("לא נמצאו קבצים בתיקיית data!")
            return None

# --- 4. אתחול ה-Pipeline ב-Session State ---
if "pipeline" not in st.session_state or st.session_state.pipeline is None:
    # ניסיון טעינה ראשוני
    pipeline = RAGPipeline()
    if not os.path.exists("faiss_index"):
        # אם אין אינדקס, נבנה אותו אוטומטית מהקבצים ב-data
        st.session_state.pipeline = rebuild_system()
    else:
        st.session_state.pipeline = pipeline

# --- 5. Sidebar - ניטור ושליטה ---
st.sidebar.header("⚙️ System Control")
if st.sidebar.button("🔄 Rebuild Index (Full Scan)"):
    st.session_state.pipeline = rebuild_system()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.info("""
**Monitoring Status:**
- Prometheus: Port 8000
- Grafana: Port 3000
""")

# הצגת רשימת הקבצים הנוכחית ב-Sidebar
if os.path.exists("./data"):
    files = [f for f in os.listdir("./data") if f.endswith(".pdf")]
    st.sidebar.write(f"📂 **Files in data folder ({len(files)}):**")
    for f in files:
        st.sidebar.caption(f"- {f}")

# --- 6. ממשק הצ'אט ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# הצגת היסטוריה
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# קלט מהמשתמש
if prompt := st.chat_input("Ask something about the candidates..."):
    # הוספת הודעת משתמש
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # קבלת תשובה מה-AI
    if st.session_state.pipeline:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.pipeline.ask_question(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
    else:
        st.error("System not initialized. Please check the data folder and rebuild.")