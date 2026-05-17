"""Pull request parsing utilities."""
from __future__ import annotations

from typing import Any, Tuple, List

from github.PullRequest import PullRequest

from app.core.exceptions import DiffProcessingError


def get_diff(pr: PullRequest) -> Tuple[str, List[str]]:
    """Return unified diff text and list of changed file paths."""
    diff = pr.raw_data.get("diff_url")
    # PyGithub exposes .get_files for changed files and .patch per file
    files = pr.get_files()
    diff_chunks: list[str] = []
    changed_files: list[str] = []
    for f in files:
        if f.patch:
            diff_chunks.append(f"diff --git a/{f.filename} b/{f.filename}\n{f.patch}")
        changed_files.append(f.filename)
    if not diff_chunks:
        raise DiffProcessingError("empty")
    return "\n".join(diff_chunks), changed_files