# mini-RAG

A modular, production-ready Retrieval-Augmented Generation (RAG) backend application built with **FastAPI** and **Python**.

---

## 📌 Features

- **Document Ingestion:** Upload and parse documents (PDF, TXT, etc.).
- **Smart Chunking:** Text extraction and chunking strategies.
- **Vector Database Indexing:** Embedding generation and storage for semantic search.
- **Semantic Search:** Fast similarity search with relevance scoring.
- **LLM Answer Generation:** Grounded context-aware answers generated via LLM.

---

## 🛠️ Requirements

- **Python:** 3.8 or higher
- **Git**

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/SERAJ316/Mini-Rag.git
cd Mini-Rag
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Environment Variables
Copy the example environment file and configure your keys:
```bash
# On Windows:
copy .env.example .env

# On Linux/macOS:
cp .env.example .env
```

### 4. Run the Application
```bash
uvicorn main:app --reload
```
The API documentation will be available at: `http://127.0.0.1:8000/docs`
