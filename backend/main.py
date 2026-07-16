import os
import sys
sys.path.append(os.path.dirname(__file__))

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import httpx
from sqlalchemy.orm import Session
from src.agent import run_agent

load_dotenv()

from src.ingestion import ingest_repo
from src.embeddings import create_vectorstore, load_vectorstore
from src.retrieval import retrieve_chunks
from src.generation import generate_answer
from database import get_db, User
from auth import (
    hash_password, verify_password, create_access_token,
    get_current_user, get_user_by_email,
    create_email_user, create_google_user
)

app = FastAPI()

# ── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://repo-oracle.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request models ─────────────────────────────────────────────────────────────
class IndexRequest(BaseModel):
    repo_url: str

class AskRequest(BaseModel):
    question: str

class SignupRequest(BaseModel):
    email: str
    name: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class GoogleAuthRequest(BaseModel):
    token: str

# ── Auth endpoints ─────────────────────────────────────────────────────────────
@app.post("/auth/signup")
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    existing = get_user_by_email(db, request.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user  = create_email_user(db, request.email, request.name, request.password)
    token = create_access_token({"sub": user.email})
    return {
        "token": token,
        "user": {"email": user.email, "name": user.name, "avatar_url": user.avatar_url}
    }


@app.post("/auth/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, request.email)
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token({"sub": user.email})
    return {
        "token": token,
        "user": {"email": user.email, "name": user.name, "avatar_url": user.avatar_url}
    }


@app.post("/auth/google")
async def google_auth(request: GoogleAuthRequest, db: Session = Depends(get_db)):
    # Verify Google ID token
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://oauth2.googleapis.com/tokeninfo?id_token={request.token}"
        )
    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid Google token")

    google_data = response.json()
    email      = google_data.get("email")
    name       = google_data.get("name")
    google_id  = google_data.get("sub")
    avatar_url = google_data.get("picture")

    # Check if user exists
    user = get_user_by_email(db, email)
    if not user:
        user = create_google_user(db, email, name, google_id, avatar_url)

    token = create_access_token({"sub": user.email})
    return {
        "token": token,
        "user": {"email": user.email, "name": user.name, "avatar_url": avatar_url}
    }


@app.get("/auth/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "email":      current_user.email,
        "name":       current_user.name,
        "avatar_url": current_user.avatar_url
    }


# ── Health ─────────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok"}


# ── RAG endpoints (protected) ──────────────────────────────────────────────────
@app.post("/index")
def index_repo(request: IndexRequest, current_user: User = Depends(get_current_user)):
    chunks = ingest_repo(request.repo_url)
     
    if len(chunks) == 0:
        raise HTTPException(
            status_code=400,
            detail="No Python files containing code could be found or parsed in this repository. Please make sure the repository contains Python (.py) code."
        )

    MAX_CHUNKS = 1000

    if len(chunks) > MAX_CHUNKS:
       raise HTTPException(
        status_code=400,
        detail=f"Repository too large ({len(chunks)} chunks). Maximum allowed is {MAX_CHUNKS}."
      )
    
    create_vectorstore(chunks)
    unique_files = list(set(c["file_path"] for c in chunks))
    return {
        "status":    "success",
        "chunks":    len(chunks),
        "files":     len(unique_files),
        "repo_name": [p for p in request.repo_url.split("/") if p][-1].replace(".git", "")
    }


@app.post("/ask")
def ask_question(request: AskRequest, current_user: User = Depends(get_current_user)):
    vectorstore = load_vectorstore()
    retrieved   = retrieve_chunks(request.question, vectorstore)
    answer      = generate_answer(request.question, retrieved)
    return {"answer": answer}

@app.post("/ask-agent")
def ask_agent(request: AskRequest, current_user: User = Depends(get_current_user)):
    answer = run_agent(request.question)
    return {"answer": answer}

@app.get("/repomap")
def repo_map(current_user: User = Depends(get_current_user)):
    vectorstore = load_vectorstore()
    results     = vectorstore.get()
    chunks      = []
    for metadata in results["metadatas"]:
        chunks.append({
            "file_path":  metadata.get("file_path", ""),
            "name":       metadata.get("name", ""),
            "type":       metadata.get("type", ""),
            "start_line": metadata.get("start_line", ""),
            "end_line":   metadata.get("end_line", ""),
        })
    return {"chunks": chunks}