"""Diff chunking utility."""
from __future__ import annotations

from typing import List

from app.core.config import settings


def chunk_diff(diff_text: str) -> List[str]:
    """Split unified diff into chunks limited by MAX_DIFF_LINES."""
    max_lines = settings.MAX_DIFF_LINES
    lines = diff_text.splitlines()
    chunks: List[str] = []
    current: list[str] = []
    for line in lines:
        current.append(line)
        if len(current) >= max_lines:
            chunks.append("\n".join(current))
            current = []
    if current:
        chunks.append("\n".join(current))
    return chunks