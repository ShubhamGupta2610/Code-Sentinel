"""Intent extraction from PR title/body and linked issues."""
from __future__ import annotations

import re
from typing import Any, List

import httpx
from github.Repository import Repository

from app.core.config import settings
from app.core.exceptions import IntentExtractionError
from app.core.logger import get_logger

ISSUE_REGEX = re.compile(r"(?:fixes|closes|resolves)\s+#(\d+)", re.IGNORECASE)


def extract_intent(pr_title: str, pr_body: str, repo: Repository) -> str:
    """Summarize developer intent in two sentences using PR + linked issue."""
    log = get_logger(repo=repo.full_name, pr_title=pr_title)
    intent_raw_parts: List[str] = [pr_title or "", pr_body or ""]

    match = ISSUE_REGEX.search(pr_body or "")
    if match:
        issue_number = int(match.group(1))
        try:
            issue = repo.get_issue(issue_number)
            intent_raw_parts.extend([issue.title or "", issue.body or ""])
        except Exception:  # noqa: BLE001
            log.warning("issue_fetch_failed", issue_number=issue_number)

    intent_raw = "\n".join(intent_raw_parts).strip()[:500]
    prompt = (
        "You are an expert reviewer. In exactly 2 sentences, summarize what this pull request intends to accomplish "
        "and the expected correct behavior after the change. Be concise, concrete, and avoid speculation.\n\n"
        f"PR + linked issue context:\n{intent_raw}"
    )
    fallback = pr_title or "No title provided"

    try:
        with httpx.Client(timeout=httpx.Timeout(20.0, connect=5.0)) as client:
            response = client.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json={"model": settings.OLLAMA_MODEL, "prompt": prompt, "stream": False},
            )
            response.raise_for_status()
            data = response.json()
            intent_summary = (data.get("response") or "").strip()
            if not intent_summary:
                log.warning("intent_llm_empty_response")
                return fallback
            return intent_summary
    except Exception as exc:  # noqa: BLE001
        log.warning("intent_llm_failed", error=str(exc))
        return fallback
