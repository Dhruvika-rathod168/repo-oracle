# 🔮 Repo-Oracle

> Ask anything about any codebase. Get answers with source citations.

Repo-Oracle is an AI-powered codebase Q&A assistant that lets you index any GitHub repository and ask natural language questions about it. Built with a FastAPI backend, React frontend, and a RAG pipeline using LangChain, ChromaDB, HuggingFace embeddings, and Groq LLM.

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

GitHub Repo URL
↓
Git Clone (GitPython)
↓
AST Parsing (function/class level chunks)
↓
HuggingFace Embeddings (all-MiniLM-L6-v2)
↓
ChromaDB Vector Store
↓
User Query
↓
├── Traditional RAG
│       ↓
│   Similarity Search (top-5 chunks)
│       ↓
│   Groq LLM → Answer + Source Citations
│
└── Agentic RAG
↓
LLM decides which tool to call
↓
┌─────────────────────┐
│ search_codebase     │ → semantic search
│ find_function       │ → find by name
│ count_chunks        │ → count stats
└─────────────────────┘
↓
Final Answer + Source Citations


## 📁 Project Structure
Repo-Oracle/
├── backend/
│   ├── src/
│   │   ├── ingestion.py      # Git clone + AST chunking
│   │   ├── embeddings.py     # HuggingFace + ChromaDB
│   │   ├── retrieval.py      # Similarity search
│   │   ├── generation.py     # LLM answer generation
│   │   └── agent.py          # Agentic RAG with tools
│   ├── main.py               # FastAPI endpoints
│   ├── auth.py               # JWT + Google OAuth
│   └── database.py           # SQLite user model
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── Login.jsx     # Auth page
│       │   ├── Sidebar.jsx   # Repo indexing + user info
│       │   ├── Chat.jsx      # Chat interface
│       │   └── RepoMap.jsx   # File tree + function explorer
│       └── App.jsx           # Main app + routing
├── requirements.txt
└── README.md

Made by [Dhruvika Rathod](https://github.com/Dhruvika-rathod168)

