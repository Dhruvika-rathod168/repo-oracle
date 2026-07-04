from __future__ import annotations

import os

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_groq import ChatGroq


MAX_CHUNK_CHARACTERS = 1200


def generate_answer(user_query: str, context_docs: list[Document]) -> str:
	"""Generate an answer from retrieved code chunks and cite the source locations."""

	load_dotenv()
	groq_api_key = os.getenv("GROQ_API_KEY")
	if not groq_api_key:
		raise ValueError("GROQ_API_KEY is missing. Set it in your .env file before calling generate_answer().")

	formatted_chunks: list[str] = []
	for index, doc in enumerate(context_docs, start=1):
		metadata = doc.metadata or {}
		file_path = metadata.get("file_path", "unknown file")
		name = metadata.get("name", "unknown function")
		chunk_header = f"Chunk {index} | file: {file_path} | function: {name}"
		chunk_text = doc.page_content.strip()
		if len(chunk_text) > MAX_CHUNK_CHARACTERS:
			chunk_text = chunk_text[:MAX_CHUNK_CHARACTERS] + "\n...[truncated]"
		formatted_chunks.append(f"{chunk_header}\n{chunk_text}")

	prompt = (
    "You are an expert code assistant helping developers understand a codebase.\n\n"
    f"User question: {user_query}\n\n"
    "Retrieved code chunks:\n"
    + "\n\n".join(formatted_chunks)
    + "\n\n"
    "Instructions:\n"
    "- Answer clearly and concisely using only the retrieved code chunks\n"
    "- Start with a one-line summary of the answer\n"
    "- Break your explanation into short paragraphs with a blank line between each\n"
    "- Cite sources at the end of each point as [source: file_path::function_name]\n"
    "- If the answer is not fully supported by the code, say so honestly\n"
    "- Do not guess or hallucinate code that is not in the retrieved chunks\n"
)

	model = ChatGroq(
		model="llama-3.3-70b-versatile",
		groq_api_key=groq_api_key,
	)
	response = model.invoke(prompt)
	return response.content if hasattr(response, "content") else str(response)
