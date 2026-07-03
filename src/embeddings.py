from __future__ import annotations

from pathlib import Path

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings


def create_vectorstore(chunk_dicts: list[dict[str, object]]) -> Chroma:
	"""Create a persisted Chroma vectorstore from chunk dictionaries."""

	documents: list[Document] = []
	for chunk in chunk_dicts:
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

	embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
	vectorstore = Chroma.from_documents(
		documents=documents,
		embedding=embeddings,
		persist_directory=".chroma",
	)

	persist = getattr(vectorstore, "persist", None)
	if callable(persist):
		persist()

	return vectorstore


def load_vectorstore() -> Chroma:
	"""Load an existing Chroma vectorstore from the .chroma directory."""

	persist_directory = Path(".chroma")
	if not persist_directory.exists():
		raise FileNotFoundError(
			"No persisted Chroma vectorstore found in '.chroma'. Create one first with create_vectorstore()."
		)

	embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
	return Chroma(persist_directory=str(persist_directory), embedding_function=embeddings)
