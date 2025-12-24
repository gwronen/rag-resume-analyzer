import os
from pathlib import Path
from dotenv import load_dotenv

# Imports המותאמים לגרסאות החדשות
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate  # <--- זה השינוי הקריטי

# Load environment variables
load_dotenv()

class RAGPipeline:
    def __init__(self, data_folder="./data", index_path="./faiss_index"):
        self.data_folder = Path(data_folder)
        self.index_path = Path(index_path)
        
        # Get OpenAI API key from environment (.env file)
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables.")
        
        # OpenAIEmbeddings automatically reads OPENAI_API_KEY from environment
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore = None
        
        # אתחול מודל השפה (LLM)
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    def load_pdfs(self):
        documents = []
        pdf_files = list(self.data_folder.glob("*.pdf"))
        if not pdf_files:
            return documents
        
        for pdf_file in pdf_files:
            try:
                loader = PyPDFLoader(str(pdf_file))
                docs = loader.load()
                documents.extend(docs)
            except Exception as e:
                print(f"Error loading {pdf_file.name}: {e}")
        return documents

    def chunk_documents(self, documents, chunk_size=1000, chunk_overlap=200):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
        return text_splitter.split_documents(documents)

    def create_and_save_index(self, chunks):
        if not chunks: return
        self.vectorstore = FAISS.from_documents(chunks, self.embeddings)
        self.vectorstore.save_local(str(self.index_path))

    def load_index(self):
        if not self.index_path.exists(): return False
        self.vectorstore = FAISS.load_local(
            str(self.index_path),
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        return True

    def ask_question(self, query, k=8):
        """
        Retrieval + Generation: מוצא את המידע ועונה תשובה אנושית.
        """
        if self.vectorstore is None:
            return "Error: Index not initialized."

        # 1. Retrieval: מציאת הקטעים הרלוונטיים (Context)
        # אם שואלים על שמות, נחפש גם באופן כללי יותר
        search_query = query
        if any(word in query.lower() for word in ['name', 'names', 'candidate', 'candidates', 'who', 'מי']):
            # חיפוש כללי יותר למציאת שמות
            search_query = query + " personal information contact details header"
            k = max(k, 10)  # יותר קטעים לחיפוש שמות
        
        docs = self.vectorstore.similarity_search(search_query, k=k)
        
        # איסוף כל המקורות הייחודיים
        unique_sources = set()
        for doc in docs:
            source = doc.metadata.get('source', '')
            if source:
                unique_sources.add(Path(source).stem)
        
        # בניית context עם מידע על המקור
        context_parts = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get('source', 'Unknown')
            page = doc.metadata.get('page', 'N/A')
            filename = Path(source).name
            context_parts.append(f"[Document {i} - File: {filename}, Page {page}]\n{doc.page_content}")
        
        context_text = "\n\n---\n\n".join(context_parts)
        
        # הוספת רשימת קבצים למידע נוסף
        if unique_sources:
            files_info = f"\nAvailable resume files: {', '.join(sorted(unique_sources))}"
            context_text = context_text + files_info

        # 2. Prompt: בניית ההנחיה ל-AI - יותר ספציפי לחילוץ מידע
        template = """You are a professional assistant analyzing resumes and documents. 
Answer the question based ONLY on the provided context. Extract specific information like names, dates, skills, etc.

When answering:
- If asked about names, list ALL names you find in the context - check the document content AND filenames
- Names are often at the top/beginning of documents
- If asked about candidates, identify each candidate by their name from the documents
- Extract names from both the document content and the file names if provided
- Be specific and extract concrete information
- If the information is not in the context, say "I don't have enough information in the provided documents"
        
Context from documents:
{context}
        
Question: {question}
        
Provide a clear, specific answer based on the context above:"""
        
        prompt = PromptTemplate(template=template, input_variables=["context", "question"])
        
        # 3. Generation: שליחה ל-OpenAI לקבלת תשובה מסוכמת
        chain = prompt | self.llm
        response = chain.invoke({"context": context_text, "question": query})
        
        return response.content

def main():
    try:
        pipeline = RAGPipeline()
    except ValueError as e:
        print(f"Error: {e}")
        return
    
    if pipeline.index_path.exists():
        print("\n[INFO] Loading existing index...")
        pipeline.load_index()
    else:
        pipeline.data_folder.mkdir(exist_ok=True)
        print("\n=== Processing Documents ===")
        documents = pipeline.load_pdfs()
        if not documents:
            print("[!] Please add PDFs to the /data folder.")
            return
        chunks = pipeline.chunk_documents(documents)
        pipeline.create_and_save_index(chunks)
        print("[SUCCESS] Index created.")

    print("\n" + "="*40)
    print("🚀 AI RAG System Ready!")
    print("Ask me anything about your documents.")
    print("="*40)
    
    while True:
        try:
            query = input("\n🔍 Your Question: ").strip()
            if query.lower() in ['exit', 'quit', 'q', 'יציאה']:
                break
            if not query: continue
            
            print("⏳ Thinking...")
            answer = pipeline.ask_question(query)
            
            print("\n📢 Answer:")
            print("-" * 30)
            print(answer)
            print("-" * 30)
            
        except Exception as e:
            print(f"\n[!] Error: {e}")

if __name__ == "__main__":
    main()