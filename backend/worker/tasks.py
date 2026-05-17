"""Celery tasks orchestrating PR review pipeline with resilience."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, TimeoutError
from datetime import datetime, timezone
from typing import Any, Dict, List

from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from github.GithubException import GithubException
from sqlalchemy.exc import SQLAlchemyError

from app.core.logger import get_logger, EVENT
from app.core.config import settings
from app.core.exceptions import DiffProcessingError
from app.db.database import SessionLocal
from app.db.models import PullRequestReview, ReviewStatus, Repository, Finding
from app.services.intent_extractor import extract_intent
from app.services.pr_parser import get_diff
from app.services.diff_processor import chunk_diff
from app.services.context_extractor import get_context
from app.services.ai_reviewer import review_chunk
from app.services.severity_ranker import rank_and_limit
from app.services.github_client import get_repo, post_inline_comments, post_summary_review, post_commit_status, post_general_comment


@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    max_retries=3,
    soft_time_limit=240,
    time_limit=300,
)
def process_pr_review(payload: Dict[str, Any]) -> None:
    """
    Full PR review pipeline:
    1) create DB record
    2) extract intent
    3) fetch diff
    4) chunk diff
    5) extract context
    6) AI review (parallel)
    7) rank findings
    8) store in DB
    9) post GitHub comments
    10) post summary
    11) update status
    """
    log = get_logger(pr_number=payload.get("pr_number"), repo=payload.get("repo_name"))
    db = SessionLocal()
    review = None

    try:
        # Fetch repo and PR objects (GitHub) with rate-limit handling
        try:
            repo = get_repo(payload["repo_owner"], payload["repo_name"], payload["installation_id"])
            pr = repo.get_pull(payload["pr_number"])
        except GithubException as exc:
            reset = exc.headers.get("X-RateLimit-Reset") if getattr(exc, "headers", None) else None
            log.error("github_api_failed", status_code=exc.status, endpoint=str(exc.data), retry_after=reset)
            if reset:
                from datetime import datetime as _dt

                eta = _dt.fromtimestamp(int(reset))
                process_pr_review.apply_async(args=[payload], eta=eta)
                return
            raise

        # Step 1: Create or attach repository record then review record
        repo_db = (
            db.query(Repository)
            .filter(Repository.owner == payload["repo_owner"], Repository.name == payload["repo_name"])
            .first()
        )
        if not repo_db:
            repo_db = Repository(owner=payload["repo_owner"], name=payload["repo_name"], installation_id=payload["installation_id"])
            db.add(repo_db)
            db.commit()
            db.refresh(repo_db)

        review = PullRequestReview(
            repo_id=repo_db.id,
            pr_number=payload["pr_number"],
            head_sha=payload["head_sha"],
            pr_title=payload["pr_title"],
            status=ReviewStatus.processing,
        )
        db.add(review)
        db.commit()
        db.refresh(review)
        log.info(EVENT["REVIEW_STARTED"], chunk_count=0, review_id=str(review.id))

        # Step 2: Extract intent
        intent_summary = extract_intent(payload["pr_title"], payload.get("pr_body", ""), repo)
        review.intent_summary = intent_summary
        db.commit()

        # Step 3: Fetch diff
        diff_text, changed_files = get_diff(pr)

        # Step 4: Chunk diff
        chunks = chunk_diff(diff_text)
        if not chunks:
            raise DiffProcessingError("empty")
        log.info(EVENT["REVIEW_STARTED"], chunk_count=len(chunks), review_id=str(review.id))

        # Step 5: Extract context (lightweight RAG)
        context_map = get_context(changed_files, repo, payload["head_sha"])

        # Step 6: AI review in parallel with per-chunk timeout
        all_results: List[Dict[str, Any]] = []
        timed_out_chunks: List[int] = []

        def run_chunk(chunk_index: int, chunk_text: str) -> Dict[str, Any]:
            context_block = context_map.get(changed_files[min(chunk_index, len(changed_files) - 1)], "")
            return review_chunk(chunk_text, intent_summary, context_block, chunk_index=chunk_index)

        def submit_chunk(idx: int, chunk: str, attempts: int = 2) -> Dict[str, Any]:
            for attempt in range(attempts):
                try:
                    return run_chunk(idx, chunk)
                except SoftTimeLimitExceeded:
                    log.warning(EVENT["CHUNK_SOFT_TIME"], chunk_index=idx, attempt=attempt + 1)
            raise SoftTimeLimitExceeded()

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(submit_chunk, idx, chunk): idx for idx, chunk in enumerate(chunks)}
            for future, idx in list(futures.items()):
                try:
                    res = future.result(timeout=90)
                    all_results.append(res)
                except TimeoutError:
                    log.warning(EVENT["CHUNK_TIMEOUT"], chunk_index=idx)
                    timed_out_chunks.append(idx)
                except SoftTimeLimitExceeded:
                    log.warning(EVENT["CHUNK_SOFT_TIME"], chunk_index=idx)
                    timed_out_chunks.append(idx)
                except Exception as exc:  # noqa: BLE001
                    log.warning("chunk_failed", chunk_index=idx, error=str(exc))

        # Partial-failure recovery: continue if at least one chunk succeeded
        if not all_results:
            raise DiffProcessingError("all_chunks_failed")
        if timed_out_chunks:
            try:
                post_general_comment(repo, payload["pr_number"], f"Review incomplete for chunks {timed_out_chunks}")
            except Exception:  # noqa: BLE001
                pass
            log.warning("llm_timeout_chunks", chunks=timed_out_chunks)

        # Step 7: Aggregate + rank findings
        merged_findings: List[Dict[str, Any]] = []
        reasoning_parts: List[str] = []
        for res in all_results:
            reasoning_parts.append(res.get("reasoning_summary", ""))
            for f in res.get("findings", []):
                merged_findings.append(
                    {
                        "severity": f.get("severity"),
                        "category": f.get("category"),
                        "file_path": f.get("file_path", ""),
                        "line": f.get("line", 1),
                        "issue_text": f.get("issue", ""),
                        "attack_scenario": f.get("attack_scenario", ""),
                        "fix_suggestion": f.get("fix", ""),
                        "confidence": f.get("confidence", 0.0),
                    }
                )

        limited, score, grade, github_state, suppressed = rank_and_limit(merged_findings)
        log.debug(EVENT["FINDINGS_PARSED"], count=len(merged_findings))

        # Apply confidence threshold for posting
        limited = [f for f in limited if float(f.get("confidence", 0.0)) >= settings.CONFIDENCE_THRESHOLD]

        # Deduplicate against existing findings in DB for this PR
        existing_keys = {
            (f.file_path, f.line_number, f.category)
            for f in db.query(Finding).filter(Finding.review_id == review.id).all()
        }
        limited = [
            f for f in limited if (f.get("file_path"), f.get("line"), f.get("category")) not in existing_keys
        ]

        # Step 8: Persist findings + reasoning
        try:
            for f in merged_findings:
                db.add(
                    Finding(
                        review_id=review.id,
                        severity=f.get("severity"),
                        category=f.get("category"),
                        file_path=f.get("file_path"),
                        line_number=f.get("line"),
                        issue_text=f.get("issue_text"),
                        attack_scenario=f.get("attack_scenario"),
                        fix_suggestion=f.get("fix_suggestion"),
                        confidence=f.get("confidence"),
                    )
                )
            review.reasoning_summary = "\n".join(reasoning_parts)
            review.score = score
            review.grade = grade
            review.status = ReviewStatus.completed
            review.completed_at = datetime.now(timezone.utc)
            db.commit()
        except SQLAlchemyError as exc:
            log.error("db_write_failed", table="findings", error=str(exc))
            try:
                post_general_comment(repo, payload["pr_number"], "Persistence failed; findings not stored in DB.")
            except Exception:  # noqa: BLE001
                pass

        # Step 9: Post inline comments (limited set)
        comment_ids: List[int] = []
        try:
            comment_ids = post_inline_comments(repo, payload["pr_number"], limited)
            log.info(EVENT["COMMENTS_POSTED"], comment_ids=comment_ids)

            # Step 10: Post summary review and commit status
            post_summary_review(repo, payload["pr_number"], grade, score, merged_findings, github_state)
            if suppressed > 0:
                post_general_comment(
                    repo,
                    payload["pr_number"],
                    f"{suppressed} additional findings suppressed. View full report at {settings.REACT_APP_API_URL}",
                )
            critical = len([f for f in merged_findings if f.get("severity") == "CRITICAL"])
            high = len([f for f in merged_findings if f.get("severity") == "HIGH"])
            post_commit_status(repo, payload["head_sha"], grade, github_state, critical, high)
        except GithubException as exc:
            reset = exc.headers.get("X-RateLimit-Reset") if getattr(exc, "headers", None) else None
            log.error(EVENT["GITHUB_API_FAILED"], status_code=exc.status, endpoint=str(exc.data), retry_after=reset)
            if reset:
                from datetime import datetime as _dt

                eta = _dt.fromtimestamp(int(reset))
                process_pr_review.apply_async(args=[payload], eta=eta)
                return
            raise

        log.info("review_completed", grade=grade, score=score, comment_ids=comment_ids)

    except DiffProcessingError as exc:
        log.warning("review_skipped", reason=str(exc))
        if review:
            review.status = ReviewStatus.skipped
            db.commit()
        try:
            post_general_comment(repo, payload["pr_number"], "No reviewable code changes detected")
            post_commit_status(repo, payload["head_sha"], grade="C", github_state="pending", critical=0, high=0)
        except Exception:  # noqa: BLE001
            pass
    except Exception as exc:  # noqa: BLE001
        log.error("review_failed", error=str(exc))
        if review:
            try:
                review.status = ReviewStatus.failed
                db.commit()
            except SQLAlchemyError as db_exc:
                log.error("db_write_failed", table="pull_request_reviews", error=str(db_exc))
        # propagate for Celery autoretry
        raise
    finally:
        db.close()
