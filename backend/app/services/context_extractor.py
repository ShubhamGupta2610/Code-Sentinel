"""Phase 1 RAG context extraction."""
from __future__ import annotations

import re
from typing import Dict, List

from github.Repository import Repository

SKIP_EXT = {"jpg", "png", "pdf", "svg", "lock", "bin"}

IMPORT_RE = re.compile(r"^\s*(import .+|from .+ import .+)")
DEF_RE = re.compile(r"^\s*(def .+\(|class .+\(|function .+\(|const .+=|let .+=|var .+=)")
CONST_RE = re.compile(r"^\s*[A-Z_][A-Z0-9_]*\s*=\s*.+")


def get_context(changed_files: List[str], repo: Repository, head_sha: str) -> Dict[str, str]:
    context: Dict[str, str] = {}
    for path in changed_files:
        ext = path.split(".")[-1].lower()
        if ext in SKIP_EXT:
            continue
        try:
            file_content = repo.get_contents(path, ref=head_sha).decoded_content.decode("utf-8", errors="ignore")
        except Exception:  # noqa: BLE001
            continue

        lines = file_content.splitlines()
        imports = [line for line in lines[:30] if IMPORT_RE.match(line)]
        signatures = [line for line in lines if DEF_RE.match(line)]
        constants = [line for line in lines if CONST_RE.match(line)]

        block_parts: List[str] = [
            f"FILE: {path}",
            "IMPORTS:",
            *imports,
            "SIGNATURES:",
            *signatures,
            "CONSTANTS:",
            *constants,
            "FILE SNIPPET:",
            *lines[:200],
        ]

        # Ensure context block is capped at 200 lines total.
        capped_block = "\n".join(block_parts[:200])
        context[path] = capped_block
    return context
