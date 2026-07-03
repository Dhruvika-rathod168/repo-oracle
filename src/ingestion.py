from __future__ import annotations

import ast
import os
from pathlib import Path
from urllib.parse import urlparse

from git import Repo


def clone_repo(repo_url: str, clone_dir: str = "repos") -> str:
	"""Clone a GitHub repository into a local directory.

	If the repository already exists locally, the existing path is returned
	without cloning again.
	"""

	target_root = Path(clone_dir)
	target_root.mkdir(parents=True, exist_ok=True)

	repo_name = Path(urlparse(repo_url).path.rstrip("/")).name
	if repo_name.endswith(".git"):
		repo_name = repo_name[:-4]

	local_path = target_root / repo_name
	if local_path.exists():
		return str(local_path)

	Repo.clone_from(repo_url, local_path)
	return str(local_path)


def get_python_files(repo_path: str) -> list[str]:
	"""Return all Python files under a repository path.

	Directories that commonly contain dependencies or generated files are skipped.
	"""

	ignored_dirs = {"venv", "node_modules", "__pycache__", ".git", "build"}
	python_files: list[str] = []

	for root, dirs, files in os.walk(repo_path):
		dirs[:] = [directory for directory in dirs if directory not in ignored_dirs]

		for file_name in files:
			if file_name.endswith(".py"):
				python_files.append(str(Path(root) / file_name))

	return python_files


def chunk_python_file(file_path: str) -> list[dict[str, object]]:
	"""Split a Python file into function and class chunks using the AST.

	Returns one dictionary per function or class definition. Files that fail to
	parse are handled gracefully by returning an empty list.
	"""

	try:
		file_text = Path(file_path).read_text(encoding="utf-8")
		tree = ast.parse(file_text)
	except (OSError, UnicodeDecodeError, SyntaxError):
		return []

	lines = file_text.splitlines()
	chunks: list[dict[str, object]] = []

	class DefinitionCollector(ast.NodeVisitor):
		def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
			chunks.append(_build_chunk(node, "function"))
			self.generic_visit(node)

		def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
			chunks.append(_build_chunk(node, "function"))
			self.generic_visit(node)

		def visit_ClassDef(self, node: ast.ClassDef) -> None:
			chunks.append(_build_chunk(node, "class"))
			self.generic_visit(node)

	def _build_chunk(node: ast.AST, chunk_type: str) -> dict[str, object]:
		start_line = getattr(node, "lineno", 0)
		end_line = getattr(node, "end_lineno", start_line)
		chunk_text = ast.get_source_segment(file_text, node)

		if chunk_text is None and start_line and end_line:
			chunk_text = "\n".join(lines[start_line - 1:end_line])

		return {
			"chunk_text": chunk_text or "",
			"file_path": file_path,
			"name": getattr(node, "name", ""),
			"type": chunk_type,
			"start_line": start_line,
			"end_line": end_line,
		}

	DefinitionCollector().visit(tree)
	return chunks


def ingest_repo(repo_url: str, clone_dir: str = "repos") -> list[dict[str, object]]:
	"""Clone a repository and collect all Python function/class chunks from it."""

	repo_path = clone_repo(repo_url, clone_dir)
	python_files = get_python_files(repo_path)
	all_chunks: list[dict[str, object]] = []

	for index, file_path in enumerate(python_files, start=1):
		print(f"Processing {index}/{len(python_files)}: {file_path}")
		all_chunks.extend(chunk_python_file(file_path))

	return all_chunks
