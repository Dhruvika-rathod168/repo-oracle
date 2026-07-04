from __future__ import annotations

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document


def retrieve_chunks(user_query: str, vectorstore: Chroma) -> list[Document]:
	"""Return the top 5 most relevant chunks for a user query."""

	if vectorstore is None:
		raise ValueError("Vectorstore is not loaded. Index a repository first.")

	return vectorstore.similarity_search(user_query, k=10)
