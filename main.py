import os
import time
import threading
from pathlib import Path
from dotenv import load_dotenv

# Imports
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate

# Watchdog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Prometheus metrics
from prometheus_client import start_http_server, Counter, Histogram, Gauge, REGISTRY

# פונקציית עזר למניעת כפילויות במטריקות
def get_metric(cls, name, desc, labelnames=None):
    if name in REGISTRY._names_to_collectors:
        return REGISTRY._names_to_collectors[name]
    if labelnames:
        return cls(name, desc, labelnames)
    return cls(name, desc)

# הגדרת המטריקות
_pdf_processed_total = get_metric(Counter, 'rag_pdf_processed_total', 'Total number of PDFs indexed')
_questions_total = get_metric(Counter, 'rag_questions_total', 'Total questions asked', ['status'])
_question_duration = get_metric(Histogram, 'rag_question_duration_seconds', 'Time spent processing questions')
_documents_loaded = get_metric(Gauge, 'rag_documents_loaded', 'Number of documents in the current session')

load_dotenv()

class RAGPipeline:
    def __init__(self, data_folder="./data", index_path="./faiss_index"):
        self.data_folder = Path(data_folder)
        self.index_path = Path(index_path)
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore = None
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.data_folder.mkdir(exist_ok=True)
        self.load_index()

    def load_pdfs(self):
        """סורק את כל תיקיית ה-data ומחזיר רשימת מסמכים"""
        all_docs = []
        if not self.data_folder.exists():
            return []
        pdf_files = [f for f in os.listdir(self.data_folder) if f.endswith(".pdf")]
        print(f"📂 Found {len(pdf_files)} PDF files: {pdf_files}")
        
        for file in pdf_files:
            try:
                loader = PyPDFLoader(str(self.data_folder / file))
                all_docs.extend(loader.load())
            except Exception as e:
                print(f"❌ Error loading {file}: {e}")
        
        _documents_loaded.set(len(pdf_files))
        return all_docs

    def chunk_documents(self, docs):
        """מפרק מסמכים לקטעים"""
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        return text_splitter.split_documents(docs)

    def create_and_save_index(self, chunks):
        """יוצר אינדקס חדש ושומר לדיסק"""
        if not chunks:
            return False
        self.vectorstore = FAISS.from_documents(chunks, self.embeddings)
        self.vectorstore.save_local(str(self.index_path))
        return True

    def process_single_pdf(self, pdf_path):
        """מעבד קובץ בודד עבור ה-Watchdog"""
        try:
            loader = PyPDFLoader(str(pdf_path))
            docs = loader.load()
            chunks = self.chunk_documents(docs)
            if self.vectorstore is None:
                self.vectorstore = FAISS.from_documents(chunks, self.embeddings)
            else:
                new_vs = FAISS.from_documents(chunks, self.embeddings)
                self.vectorstore.merge_from(new_vs)
            self.vectorstore.save_local(str(self.index_path))
            _pdf_processed_total.inc()
            pdf_count = len([f for f in os.listdir(self.data_folder) if f.endswith(".pdf")])
            _documents_loaded.set(pdf_count)
        except Exception as e:
            print(f"❌ Error: {e}")

    def load_index(self):
        """טוען אינדקס קיים מהדיסק"""
        if self.index_path.exists():
            try:
                self.vectorstore = FAISS.load_local(
                    str(self.index_path), self.embeddings, allow_dangerous_deserialization=True
                )
                pdf_files = len([f for f in os.listdir(self.data_folder) if f.endswith(".pdf")])
                _documents_loaded.set(pdf_files)
                return True
            except:
                return False
        return False

    def ask_question(self, query):
        """מבצע חיפוש ועונה על השאלה עם ציון המקורות"""
        if self.vectorstore is None:
            return "No documents indexed yet."

        start_time = time.time()
        # שליפת 10 קטעים כדי לוודא שכל המועמדים נלקחים בחשבון
        docs = self.vectorstore.similarity_search(query, k=10)
        
        context_parts = []
        found_sources = set()

        for d in docs:
            source_path = d.metadata.get('source', 'Unknown')
            file_name = os.path.basename(source_path)
            found_sources.add(file_name)
            context_parts.append(f"Source [{file_name}]:\n{d.page_content}")
        
        context = "\n\n".join(context_parts)
        
        template = """You are a professional HR recruiter. 
        You have access to resumes from {num_docs} candidates: {sources}.
        Use the provided context to answer the question accurately.
        
        Context:
        {context}

        Question: {question}
        
        Helpful Answer:"""
        
        prompt = PromptTemplate(
            template=template, 
            input_variables=["context", "question", "num_docs", "sources"]
        )
        
        try:
            chain = prompt | self.llm
            response = chain.invoke({
                "context": context, 
                "question": query,
                "num_docs": len(found_sources),
                "sources": ", ".join(found_sources)
            })
            
            _question_duration.observe(time.time() - start_time)
            _questions_total.labels(status='success').inc()
            return response.content
        except Exception as e:
            _questions_total.labels(status='error').inc()
            return f"Error: {e}"

# --- Watchdog Logic ---
class PDFWatchdog(FileSystemEventHandler):
    def __init__(self, pipeline):
        self.pipeline = pipeline
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".pdf"):
            time.sleep(1)
            self.pipeline.process_single_pdf(event.src_path)

def start_watchdog(pipeline):
    event_handler = PDFWatchdog(pipeline)
    observer = Observer()
    observer.schedule(event_handler, str(pipeline.data_folder), recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    pipeline = RAGPipeline()
    start_http_server(8000)
    watchdog_thread = threading.Thread(target=start_watchdog, args=(pipeline,), daemon=True)
    watchdog_thread.start()
    print("🚀 System Ready!")
    while True:
        query = input("\n🔍 Question: ")
        if query.lower() in ['q', 'exit']: break
        print(f"\n📢 Answer: {pipeline.ask_question(query)}")