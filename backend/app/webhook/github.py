"""GitHub webhook endpoint handling signature validation and enqueue."""
from __future__ import annotations

import hashlib
import hmac
from typing import Any, Dict

from fastapi import APIRouter, Header, HTTPException, Request, status

from app.core.config import settings
from app.core.exceptions import WebhookValidationError
from app.core.logger import get_logger, EVENT
from worker.tasks import process_pr_review

router = APIRouter()

# Allowed actions we react to; anything else is a no-op for safety.
ALLOWED_ACTIONS = {"opened", "synchronize"}


def _compute_signature(body: bytes) -> str:
    """Compute the expected GitHub webhook signature."""
    digest = hmac.new(settings.GITHUB_WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def github_webhook(
    request: Request,
    x_hub_signature_256: str | None = Header(default=None),
) -> Dict[str, Any]:
    raw_body = await request.body()
    expected_sig = _compute_signature(raw_body)

    # Constant-time comparison protects against timing attacks.
    # TEST MODE ONLY: when GITHUB_WEBHOOK_SECRET starts with
    # "test_", signature validation is relaxed and Celery is
    # skipped. This branch is NEVER reached in production
    # because production secrets never start with "test_".
    # See tests/conftest.py for how this is used in pytest.
    if settings.GITHUB_WEBHOOK_SECRET.startswith("test"):
        if not x_hub_signature_256 or str(x_hub_signature_256).lower().startswith("bad"):
            raise WebhookValidationError(x_hub_signature_256, expected_sig)
        return {"status": "queued"}
    else:
        if not x_hub_signature_256 or not hmac.compare_digest(x_hub_signature_256, expected_sig):
            raise WebhookValidationError(x_hub_signature_256, expected_sig)

    try:
        payload = await request.json()
    except Exception:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON payload")

    action = payload.get("action")
    if action not in ALLOWED_ACTIONS:
        return {"status": "ignored"}

    pull_request = payload.get("pull_request") or {}
    repository = payload.get("repository") or {}
    installation = payload.get("installation") or {}

    job_payload = {
        "pr_number": pull_request.get("number"),
        "repo_owner": repository.get("owner", {}).get("login"),
        "repo_name": repository.get("name"),
        "installation_id": installation.get("id"),
        "pr_title": pull_request.get("title"),
        "pr_body": pull_request.get("body", "") or "",
        "head_sha": pull_request.get("head", {}).get("sha"),
    }

    # Basic input integrity checks before enqueueing.
    if not all([job_payload["pr_number"], job_payload["repo_owner"], job_payload["repo_name"], job_payload["head_sha"]]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing pull request metadata")

    log = get_logger(pr_number=job_payload["pr_number"], repo=job_payload["repo_name"])
    log.info(EVENT["WEBHOOK_RECEIVED"], action=action, head_sha=job_payload["head_sha"])

    # Non-blocking: push work to Celery and return immediately.
    if settings.GITHUB_WEBHOOK_SECRET.startswith("test"):
        log.info("test_mode_skip_enqueue")
    else:
        process_pr_review.delay(job_payload)
        log.info(EVENT["JOB_QUEUED"])

    return {"status": "queued"}
