# 🔮 Repo-Oracle

> Ask anything about any codebase. Get answers with source citations.

Repo-Oracle is an AI-powered codebase Q&A assistant that lets you index any GitHub repository and ask natural language questions about it. Built with a FastAPI backend, React frontend, and a RAG pipeline using LangChain, ChromaDB, HuggingFace embeddings, and Groq LLM.

---
## 🌐 Live Demo

**Try the application here:**  
[https://repo-oracle.vercel.app/](https://repo-oracle.vercel.app/)

---
## ✨ Features

- **AST-based code chunking** — parses Python files by function/class boundaries instead of naive text splitting
- **Traditional RAG mode** — fast semantic search + LLM answer generation with source citations
- **Agentic RAG mode** — LLM autonomously decides which tools to call (search, find function, count) before answering
- **Repo Map** — visual file tree and function/class explorer for any indexed repo
- **Persistent chat history** — chat survives switching between views

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React, Vite, Axios |
| Backend | FastAPI, Uvicorn |
| RAG Pipeline | LangChain, LangGraph |
| Embeddings | HuggingFace `all-MiniLM-L6-v2` |
| Vector DB | ChromaDB |
| LLM | Groq (LLaMA 3.3 70B) |
| Auth | JWT, Google OAuth, SQLite |
| Code Parsing | Python `ast` module |

---
## 🏗️ Architecture

```text
GitHub Repository
        │
        ▼
 Clone Repository
        │
        ▼
 AST Parsing
(Function/Class Chunking)
        │
        ▼
Generate Embeddings
(HuggingFace MiniLM)
        │
        ▼
Store in ChromaDB
        │
        ▼
──────── User Query ────────
        │
        ├──────── Traditional RAG
        │             │
        │             ▼
        │     Similarity Search
        │             │
        │             ▼
        │        Groq LLM
        │             │
        │             ▼
        │     Answer + Citations
        │
        └──────── Agentic RAG
                      │
          ┌───────────┼────────────┐
          ▼           ▼            ▼
search_codebase  find_function  count_chunks
          │           │            │
          └───────────┴────────────┘
                      │
                      ▼
          Final Answer + Citations
```

## 📁 Project Structure

```text
Repo-Oracle
├── backend/
│   ├── src/
│   │   ├── ingestion.py
│   │   ├── embeddings.py
│   │   ├── retrieval.py
│   │   ├── generation.py
│   │   ├── agent.py
│   │   ├── auth.py
│   │   └── main.py
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── App.jsx
│
├── README.md
└── requirements.txt
```



Made by [Dhruvika Rathod](https://github.com/Dhruvika-rathod168)

