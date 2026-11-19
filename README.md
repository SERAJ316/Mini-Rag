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
- **Docker** & **Docker Compose**

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

### 4. Run Docker Compose Services (MongoDB)

Navigate to the `docker` directory, copy the example environment file, and set your MongoDB credentials:

```bash
cd docker

# On Windows:
copy .env.example .env

# On Linux/macOS:
cp .env.example .env
```

Update `docker/.env` with your chosen `MONGO_INITDB_ROOT_USERNAME` and `MONGO_INITDB_ROOT_PASSWORD`, then start MongoDB in the background:

```bash
docker compose up -d
```

> Make sure `MONGODB_URL` in the root `.env` matches your credentials, e.g.:
> `MONGODB_URL="mongodb://<username>:<password>@localhost:27017"`

### 5. Run the Application
```bash
uvicorn main:app --reload
```
The API documentation will be available at: `http://127.0.0.1:8000/docs`
