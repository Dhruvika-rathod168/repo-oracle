from __future__ import annotations

import ast
import gc
import io
import os
import shutil
import urllib.request
import zipfile
from pathlib import Path
from urllib.parse import urlparse

# -----------------------------
# Configuration
# -----------------------------
MAX_FILES = 250
MAX_CHUNKS = 1000
MAX_FILE_SIZE = 500 * 1024  # 500 KB


def clone_repo(repo_url: str, clone_dir: str = "repos") -> str:
    """Clone a GitHub repository into a local directory by downloading its ZIP archive."""

    target_root = Path(clone_dir)
    target_root.mkdir(parents=True, exist_ok=True)

    # Parse owner and repository name
    parsed = urlparse(repo_url)
    path_parts = [p for p in parsed.path.split('/') if p]
    if len(path_parts) < 2:
        raise ValueError(f"Invalid GitHub repository URL: {repo_url}")

    owner = path_parts[0]
    repo_name = path_parts[1]
    if repo_name.endswith(".git"):
        repo_name = repo_name[:-4]

    branch = None
    if len(path_parts) >= 4 and path_parts[2] == "tree":
        branch = "/".join(path_parts[3:])

    local_path = target_root / repo_name

    if local_path.exists():
        shutil.rmtree(local_path, ignore_errors=True)

    # Construct candidate ZIP URLs
    urls_to_try = []
    if branch:
        urls_to_try.append(f"https://github.com/{owner}/{repo_name}/archive/refs/heads/{branch}.zip")
        urls_to_try.append(f"https://github.com/{owner}/{repo_name}/archive/refs/tags/{branch}.zip")

    urls_to_try.extend([
        f"https://github.com/{owner}/{repo_name}/archive/refs/heads/main.zip",
        f"https://github.com/{owner}/{repo_name}/archive/refs/heads/master.zip",
        f"https://api.github.com/repos/{owner}/{repo_name}/zipball"
    ])

    import tempfile
    
    # Download ZIP directly to a temp file on disk instead of memory to avoid out-of-memory errors
    temp_zip_file = tempfile.NamedTemporaryFile(delete=False, suffix=".zip", dir=str(target_root))
    temp_zip_path = Path(temp_zip_file.name)
    temp_zip_file.close()

    success = False
    last_error = None

    for url in urls_to_try:
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Repo-Oracle/1.0"}
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                if response.status == 200:
                    with open(temp_zip_path, "wb") as f:
                        shutil.copyfileobj(response, f)
                    success = True
                    break
        except Exception as e:
            last_error = e

    if not success:
        if temp_zip_path.exists():
            temp_zip_path.unlink()
        raise ValueError(
            f"Failed to download repository ZIP from GitHub for {repo_url}. "
            f"Error: {last_error}"
        )

    # Extract the ZIP to a temporary directory inside target_root, then move it to local_path
    with tempfile.TemporaryDirectory(dir=str(target_root)) as temp_dir:
        with zipfile.ZipFile(temp_zip_path) as z:
            z.extractall(path=temp_dir)

        # Locate the root directory within the zip file
        extracted_dirs = [d for d in Path(temp_dir).iterdir() if d.is_dir()]
        if not extracted_dirs:
            if temp_zip_path.exists():
                temp_zip_path.unlink()
            raise ValueError("No directory found in the extracted repository ZIP")

        extracted_path = extracted_dirs[0]
        shutil.move(str(extracted_path), str(local_path))

    if temp_zip_path.exists():
        temp_zip_path.unlink()

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


def chunk_python_file(file_path: str, repo_path: str | None = None) -> list[dict[str, object]]:
    """Split a Python file into AST chunks."""

    try:
        file_text = Path(file_path).read_text(encoding="utf-8")
        tree = ast.parse(file_text)
    except (OSError, UnicodeDecodeError, SyntaxError):
        return []

    lines = file_text.splitlines()
    chunks: list[dict[str, object]] = []

    display_path = file_path
    if repo_path:
        try:
            display_path = str(Path(file_path).relative_to(Path(repo_path))).replace("\\", "/")
        except ValueError:
            pass

    def build_chunk(node: ast.AST, chunk_type: str):
        start_line = getattr(node, "lineno", 0)
        end_line = getattr(node, "end_lineno", start_line)

        chunk_text = ast.get_source_segment(file_text, node)

        if chunk_text is None and start_line and end_line:
            chunk_text = "\n".join(lines[start_line - 1:end_line])

        return {
            "chunk_text": chunk_text or "",
            "file_path": display_path,
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


def chunk_python_file_by_lines(file_path: str, repo_path: str | None = None) -> list[dict[str, object]]:
    """Split a Python file into line-based chunks if AST chunking is not possible or yields nothing."""

    try:
        file_text = Path(file_path).read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []

    lines = file_text.splitlines()
    if not lines:
        return []

    chunks: list[dict[str, object]] = []

    display_path = file_path
    if repo_path:
        try:
            display_path = str(Path(file_path).relative_to(Path(repo_path))).replace("\\", "/")
        except ValueError:
            pass

    chunk_size = 40
    overlap = 5
    total = len(lines)

    i = 0
    while i < total:
        start_line = i + 1
        end_line = min(i + chunk_size, total)
        chunk_text = "\n".join(lines[i:end_line])

        chunks.append({
            "chunk_text": chunk_text,
            "file_path": display_path,
            "name": f"{Path(file_path).name} (Lines {start_line}-{end_line})",
            "type": "code",
            "start_line": start_line,
            "end_line": end_line,
        })

        i += max(1, chunk_size - overlap)

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

        chunks = chunk_python_file(file_path, repo_path=repo_path)
        if not chunks:
            chunks = chunk_python_file_by_lines(file_path, repo_path=repo_path)

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

        symbols = []
        if file_path in python_files:
            symbols = chunk_python_file(file_path, repo_path=repo_path)
            if not symbols:
                symbols = chunk_python_file_by_lines(file_path, repo_path=repo_path)

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