from __future__ import annotations

import gc
import shutil
from pathlib import Path

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

# Load embedding model only once when server starts
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

PERSIST_DIR = ".chroma"
BATCH_SIZE = 64


def create_vectorstore(chunk_dicts: list[dict[str, object]]) -> Chroma:
    """Create a persisted Chroma vectorstore."""

    # Remove previous database
    persist_path = Path(PERSIST_DIR)
    if persist_path.exists():
        shutil.rmtree(persist_path)

    # Create empty Chroma database
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