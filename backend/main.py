import os
import sys
sys.path.append(os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from src.ingestion import ingest_repo
from src.embeddings import create_vectorstore, load_vectorstore
from src.retrieval import retrieve_chunks
from src.generation import generate_answer

app = FastAPI()

# ── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request models ─────────────────────────────────────────────────────────────
class IndexRequest(BaseModel):
    repo_url: str

class AskRequest(BaseModel):
    question: str

# ── Endpoints ──────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/index")
def index_repo(request: IndexRequest):
    chunks = ingest_repo(request.repo_url)
    create_vectorstore(chunks)
    unique_files = list(set(c["file_path"] for c in chunks))
    return {
        "status":  "success",
        "chunks":  len(chunks),
        "files":   len(unique_files),
        "repo_name": request.repo_url.split("/")[-1].replace(".git", "")
    }


@app.post("/ask")
def ask_question(request: AskRequest):
    vectorstore     = load_vectorstore()
    retrieved       = retrieve_chunks(request.question, vectorstore)
    answer          = generate_answer(request.question, retrieved)
    return {"answer": answer}


@app.get("/repomap")
def repo_map():
    vectorstore = load_vectorstore()
    results     = vectorstore.get()
    chunks      = []
    for i, metadata in enumerate(results["metadatas"]):
        chunks.append({
            "file_path":  metadata.get("file_path", ""),
            "name":       metadata.get("name", ""),
            "type":       metadata.get("type", ""),
            "start_line": metadata.get("start_line", ""),
            "end_line":   metadata.get("end_line", ""),
        })
    return {"chunks": chunks}