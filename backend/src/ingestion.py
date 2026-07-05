from __future__ import annotations

import ast
import gc
import os
import shutil
from pathlib import Path
from urllib.parse import urlparse

from git import Repo

# -----------------------------
# Configuration
# -----------------------------
MAX_FILES = 250
MAX_CHUNKS = 1000
MAX_FILE_SIZE = 500 * 1024  # 500 KB


def clone_repo(repo_url: str, clone_dir: str = "repos") -> str:
    """Clone a GitHub repository into a local directory."""

    target_root = Path(clone_dir)
    target_root.mkdir(parents=True, exist_ok=True)

    repo_name = Path(urlparse(repo_url).path.rstrip("/")).name
    if repo_name.endswith(".git"):
        repo_name = repo_name[:-4]

    local_path = target_root / repo_name

    if local_path.exists():
        shutil.rmtree(local_path, ignore_errors=True)

    Repo.clone_from(repo_url, local_path)

    return str(local_path)


def get_python_files(repo_path: str) -> list[str]:
    """Return all Python files under a repository path."""

    ignored_dirs = {
        "venv",
        "node_modules",
        "__pycache__",
        ".git",
        "build",
    }

    python_files: list[str] = []

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [
            directory
            for directory in dirs
            if directory not in ignored_dirs
        ]

        for file_name in files:
            if not file_name.endswith(".py"):
                continue

            path = Path(root) / file_name

            try:
                if path.stat().st_size > MAX_FILE_SIZE:
                    continue
            except OSError:
                continue

            python_files.append(str(path))

    return python_files


def get_repo_files(repo_path: str) -> list[str]:
    """Return all files under a repository path."""

    ignored_dirs = {
        "venv",
        "node_modules",
        "__pycache__",
        ".git",
        "build",
    }

    repo_files: list[str] = []

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [
            directory
            for directory in dirs
            if directory not in ignored_dirs
        ]

        for file_name in files:
            repo_files.append(str(Path(root) / file_name))

    return repo_files


def chunk_python_file(file_path: str) -> list[dict[str, object]]:
    """Split a Python file into AST chunks."""

    try:
        file_text = Path(file_path).read_text(encoding="utf-8")
        tree = ast.parse(file_text)
    except (OSError, UnicodeDecodeError, SyntaxError):
        return []

    lines = file_text.splitlines()
    chunks: list[dict[str, object]] = []

    def build_chunk(node: ast.AST, chunk_type: str):
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

    class DefinitionCollector(ast.NodeVisitor):
        def visit_FunctionDef(self, node):
            chunks.append(build_chunk(node, "function"))
            self.generic_visit(node)

        def visit_AsyncFunctionDef(self, node):
            chunks.append(build_chunk(node, "function"))
            self.generic_visit(node)

        def visit_ClassDef(self, node):
            chunks.append(build_chunk(node, "class"))
            self.generic_visit(node)

    DefinitionCollector().visit(tree)

    return chunks


def ingest_repo(repo_url: str, clone_dir: str = "repos") -> list[dict[str, object]]:
    """Clone repository and create AST chunks."""

    repo_path = clone_repo(repo_url, clone_dir)

    python_files = get_python_files(repo_path)

    if len(python_files) > MAX_FILES:
        shutil.rmtree(repo_path, ignore_errors=True)
        raise ValueError(
            f"Repository too large ({len(python_files)} Python files). "
            f"Maximum supported is {MAX_FILES}."
        )

    all_chunks: list[dict[str, object]] = []

    for index, file_path in enumerate(python_files, start=1):

        print(f"Processing {index}/{len(python_files)}: {file_path}")

        chunks = chunk_python_file(file_path)

        all_chunks.extend(chunks)

        del chunks
        gc.collect()

        if len(all_chunks) >= MAX_CHUNKS:
            all_chunks = all_chunks[:MAX_CHUNKS]
            print(f"Maximum chunk limit ({MAX_CHUNKS}) reached.")
            break

    shutil.rmtree(repo_path, ignore_errors=True)

    return all_chunks


def _insert_file_into_tree(
    tree: dict[str, object],
    relative_parts: list[str],
    file_record: dict[str, object],
) -> None:

    if not relative_parts:
        tree.setdefault("files", []).append(file_record)
        return

    folders = tree.setdefault("folders", {})

    folder_name = relative_parts[0]

    child = folders.setdefault(
        folder_name,
        {
            "folders": {},
            "files": [],
        },
    )

    _insert_file_into_tree(child, relative_parts[1:], file_record)


def build_repo_map(repo_url: str, clone_dir: str = "repos") -> dict[str, object]:
    """Clone repository and build repo map."""

    repo_path = clone_repo(repo_url, clone_dir)

    repo_root = Path(repo_path)

    all_files = get_repo_files(repo_path)
    python_files = set(get_python_files(repo_path))

    records: list[dict[str, object]] = []

    tree: dict[str, object] = {
        "folders": {},
        "files": [],
    }

    total_functions = 0
    total_classes = 0

    for file_path in all_files:

        relative_path = str(Path(file_path).relative_to(repo_root))

        symbols = chunk_python_file(file_path) if file_path in python_files else []

        functions = [s for s in symbols if s["type"] == "function"]
        classes = [s for s in symbols if s["type"] == "class"]

        total_functions += len(functions)
        total_classes += len(classes)

        file_record = {
            "file_path": file_path,
            "relative_path": relative_path,
            "file_name": Path(file_path).name,
            "extension": Path(file_path).suffix.lower(),
            "is_python": file_path in python_files,
            "symbols": symbols,
            "functions": functions,
            "classes": classes,
            "function_count": len(functions),
            "class_count": len(classes),
            "symbol_count": len(symbols),
        }

        records.append(file_record)

        _insert_file_into_tree(
            tree,
            list(Path(relative_path).parts),
            file_record,
        )

    shutil.rmtree(repo_path, ignore_errors=True)

    return {
        "repo_url": repo_url,
        "repo_path": repo_path,
        "all_files": records,
        "python_files": [r for r in records if r["is_python"]],
        "tree": tree,
        "stats": {
            "total_files": len(records),
            "python_files": len(python_files),
            "functions": total_functions,
            "classes": total_classes,
        },
    }