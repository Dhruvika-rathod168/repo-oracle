from __future__ import annotations

import gc
import os
import shutil
from pathlib import Path

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_huggingface.embeddings import HuggingFaceEndpointEmbeddings

def get_embeddings():
    """Get the embeddings model (hosted on Hugging Face API if token exists, fallback to local)."""
    hf_token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACEHUB_API_TOKEN")
    if hf_token:
        print("Using Hugging Face hosted serverless Inference API for embeddings (memory optimization).")
        return HuggingFaceEndpointEmbeddings(
            model="sentence-transformers/all-MiniLM-L6-v2",
            task="feature-extraction",
            huggingfacehub_api_token=hf_token
        )
    print("Warning: HF_TOKEN not found. Falling back to local HuggingFaceEmbeddings (high RAM usage).")
    return HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

# Load embedding model only once when server starts
embeddings = get_embeddings()

PERSIST_DIR = ".chroma"
BATCH_SIZE = 64


def create_vectorstore(chunk_dicts: list[dict[str, object]]) -> Chroma:
    """Create a persisted Chroma vectorstore."""

    # Initialize the Chroma database connection
    vectorstore = Chroma(
        persist_directory=PERSIST_DIR,
        embedding_function=embeddings,
    )

    # Clear previous collection data if any exists, without deleting the directory containing sqlite
    try:
        vectorstore.delete_collection()
    except Exception as e:
        print(f"No collection to delete or error deleting: {e}")

    # Re-initialize vectorstore to ensure a fresh, empty collection is ready
    vectorstore = Chroma(
        persist_directory=PERSIST_DIR,
        embedding_function=embeddings,
    )

    # Add documents in batches
    for start in range(0, len(chunk_dicts), BATCH_SIZE):

        batch = chunk_dicts[start:start + BATCH_SIZE]

        documents = []

        for chunk in batch:
            metadata = {
                "file_path": chunk.get("file_path", ""),
                "name": chunk.get("name", ""),
                "type": chunk.get("type", ""),
                "start_line": int(chunk.get("start_line", 0) or 0),
                "end_line": int(chunk.get("end_line", 0) or 0),
            }

            documents.append(
                Document(
                    page_content=str(chunk.get("chunk_text", "")),
                    metadata=metadata,
                )
            )

        vectorstore.add_documents(documents)

        # Free memory immediately
        del documents
        gc.collect()

    persist = getattr(vectorstore, "persist", None)
    if callable(persist):
        persist()

    return vectorstore


def load_vectorstore() -> Chroma:
    """Load existing vectorstore."""

    persist_path = Path(PERSIST_DIR)

    if not persist_path.exists():
        raise FileNotFoundError(
            "No persisted Chroma vectorstore found."
        )

    return Chroma(
        persist_directory=PERSIST_DIR,
        embedding_function=embeddings,
    )