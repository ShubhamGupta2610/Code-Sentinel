"""GitHub client helpers for posting comments and statuses."""
from __future__ import annotations

import datetime
from typing import Any, Dict, List
import ssl
import redis
from github import Github, GithubIntegration
from github.Repository import Repository

from app.core.config import settings
from app.core.logger import get_logger

redis_client = redis.Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    ssl_cert_reqs=ssl.CERT_NONE,
)

# Severity emojis per spec
EMOJI = {
    "CRITICAL": "🔴",
    "HIGH": "🟠",
    "MEDIUM": "🟡",
    "INFO": "🔵",
    "INTENT_MISMATCH": "🟣",
}


def _get_installation_token(installation_id: int) -> str:
    cache_key = f"gh_token:{installation_id}"
    cached = redis_client.get(cache_key)
    if cached:
        return cached

    private_key = settings.GITHUB_PRIVATE_KEY.replace("\\n", "\n")

    integration = GithubIntegration(
        int(settings.GITHUB_APP_ID),
        private_key
    )

    token = integration.get_access_token(installation_id).token
    redis_client.setex(cache_key, datetime.timedelta(minutes=55), token)
    return token


def get_repo(owner: str, name: str, installation_id: int) -> Repository:
    token = _get_installation_token(installation_id)
    gh = Github(login_or_token=token)
    cache_key = f"repo:{owner}/{name}"
    cached = redis_client.get(cache_key)
    if cached:
        return gh.get_repo(cached)
    repo = gh.get_repo(f"{owner}/{name}")
    redis_client.setex(cache_key, datetime.timedelta(minutes=5), repo.full_name)
    return repo


def post_general_comment(repo: Repository, pr_number: int, body: str) -> None:
    pr = repo.get_pull(pr_number)
    pr.create_issue_comment(body)


def post_inline_comments(repo: Repository, pr_number: int, findings: List[Dict[str, Any]]) -> List[int]:
    pr = repo.get_pull(pr_number)
    comment_ids: List[int] = []
    for f in findings:
        body = (
            f"{EMOJI.get(f.get('severity'), '🔵')} {f.get('category')}\n"
            f"{f.get('issue_text', f.get('issue'))}\n\n"
            f"{f.get('fix_suggestion', f.get('fix', ''))}"
        )
        try:
            comment = pr.create_review_comment(
                body=body,
                commit_id=pr.head.sha,
                path=f.get("file_path", ""),
                line=f.get("line", 1),
            )
            comment_ids.append(comment.id)
        except Exception as exc:  # noqa: BLE001
            get_logger().warning("comment_post_failed", error=str(exc))
    return comment_ids


def post_summary_review(
    repo: Repository,
    pr_number: int,
    grade: str,
    score: float,
    findings: List[Dict[str, Any]],
    github_state: str,
) -> None:
    pr = repo.get_pull(pr_number)
    critical = len([f for f in findings if f.get("severity") == "CRITICAL"])
    high = len([f for f in findings if f.get("severity") == "HIGH"])
    medium = len([f for f in findings if f.get("severity") == "MEDIUM"])
    info = len([f for f in findings if f.get("severity") == "INFO"])
    body = (
        f"| Severity | Count |\n"
        f"| --- | --- |\n"
        f"| 🔴 CRITICAL | {critical} |\n"
        f"| 🟠 HIGH | {high} |\n"
        f"| 🟡 MEDIUM | {medium} |\n"
        f"| 🔵 INFO | {info} |\n\n"
        f"Dashboard: {settings.REACT_APP_API_URL}"
    )
    title = f"CodeSentinel Review — Grade: {grade}"
    event = "REQUEST_CHANGES" if critical or high else "COMMENT"
    pr.create_review(body=title + "\n\n" + body, event=event)


def post_commit_status(repo: Repository, head_sha: str, grade: str, github_state: str, critical: int, high: int) -> None:
    commit = repo.get_commit(head_sha)
    description = f"Grade {grade} — {critical} critical, {high} high"
    commit.create_status(state=github_state, description=description, context=settings.STATUS_CONTEXT)
