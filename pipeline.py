from __future__ import annotations

from src.embeddings import create_vectorstore, load_vectorstore
from src.generation import generate_answer
from src.ingestion import ingest_repo
from src.retrieval import retrieve_chunks


def run_pipeline(repo_url: str, question: str | None = None) -> str:
	"""Index a repository and optionally run the full RAG pipeline."""

	chunks = ingest_repo(repo_url)
	create_vectorstore(chunks)
	if not question:
		return ""

	vectorstore = load_vectorstore()
	retrieved_chunks = retrieve_chunks(question, vectorstore)
	answer = generate_answer(question, retrieved_chunks)
	print(answer)
	return answer


if __name__ == "__main__":
	test_repo_url = "https://github.com/<username>/<repo_name>.git"
	test_question = "What does the main package code do and how is it organized?"
	run_pipeline(test_repo_url, test_question)
