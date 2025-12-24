# RAG Resume Analyzer

A Retrieval-Augmented Generation (RAG) application for analyzing resumes using Streamlit, LangChain, OpenAI, and FAISS.

## Features

- 📄 **PDF Document Loading**: Loads PDF resumes from the `./data` folder
- ✂️ **Text Chunking**: Uses RecursiveCharacterTextSplitter to split documents into manageable chunks
- 🤖 **OpenAI Embeddings**: Generates embeddings using OpenAI's embedding model
- 💾 **FAISS Vector Store**: Stores embeddings in a local FAISS index for efficient similarity search
- 🔍 **Question-Answering**: Ask questions about the resumes and get AI-powered answers
- 🎨 **Streamlit UI**: Beautiful, user-friendly web interface

## Setup

1. **Clone the repository** (or download the code)

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the project root:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Add PDF files**:
   Place your resume PDF files in the `./data` folder

5. **Run the application**:
   ```bash
   streamlit run app.py
   ```

   The app will automatically:
   - Load PDFs from the `./data` folder
   - Create chunks and generate embeddings
   - Build a FAISS index (saved to `./faiss_index`)
   - Start the web interface at `http://localhost:8501`

## Usage

1. Open the Streamlit app in your browser
2. Wait for initialization to complete
3. Ask questions about the resumes, for example:
   - "What are the names of the candidates?"
   - "What are the skills of the candidates?"
   - "Tell me about the work experience"

## Project Structure

```
my-rag-project/
├── app.py              # Streamlit web application
├── main.py             # RAG pipeline implementation
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (not committed)
├── data/              # PDF files folder
├── faiss_index/       # FAISS vector store (generated)
└── README.md          # This file
```

## Technologies

- **LangChain**: Framework for building LLM applications
- **OpenAI**: For embeddings and chat models
- **FAISS**: Vector similarity search
- **Streamlit**: Web UI framework
- **PyPDF**: PDF document loading

## License

MIT

