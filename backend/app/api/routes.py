"""REST API for dashboard consumption."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
import redis
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Repository, PullRequestReview, Finding, Feedback, FeedbackAction
from app.core.config import settings
from app.core.logger import get_logger
from app.models.schemas import PullRequestReviewSchema, RepositorySchema

router = APIRouter()
log = get_logger(service="codesentinel-api")


@router.get("/reviews")
def list_reviews(limit: int = 20, offset: int = 0, db: Session = Depends(get_db)) -> dict[str, Any]:
    q = db.query(PullRequestReview).order_by(PullRequestReview.created_at.desc())
    reviews = q.offset(offset).limit(limit).all()
    serialized = [PullRequestReviewSchema.model_validate(r).model_dump() for r in reviews]
    return {"data": serialized, "error": None}


@router.get("/reviews/{review_id}")
def get_review(review_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    review = db.get(PullRequestReview, review_id)
    if not review:
        raise HTTPException(status_code=404, detail={"error": {"code": "NOT_FOUND", "message": "Review not found"}})
    return {"data": PullRequestReviewSchema.model_validate(review).model_dump(), "error": None}


@router.get("/repos")
def list_repos(db: Session = Depends(get_db)) -> dict[str, Any]:
    repos = db.query(Repository).all()
    serialized = [RepositorySchema.model_validate(r).model_dump() for r in repos]
    return {"data": serialized, "error": None}


@router.get("/repos/{repo_id}/trend")
def repo_trend(repo_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    reviews = (
        db.query(PullRequestReview)
        .filter(PullRequestReview.repo_id == repo_id)
        .order_by(PullRequestReview.created_at.desc())
        .limit(30)
        .all()
    )
    serialized = [PullRequestReviewSchema.model_validate(r).model_dump() for r in reviews]
    return {"data": serialized, "error": None}


@router.get("/stats/summary")
def stats_summary(db: Session = Depends(get_db)) -> dict[str, Any]:
    total_reviews = db.query(func.count(PullRequestReview.id)).scalar() or 0
    total_findings = db.query(func.count(Finding.id)).scalar() or 0
    active_repos = db.query(func.count(func.distinct(PullRequestReview.repo_id))).scalar() or 0
    avg_score = db.query(func.avg(PullRequestReview.score)).scalar() or 0
    return {"data": {"total_reviews": total_reviews, "total_findings": total_findings, "active_repos": active_repos, "avg_score": avg_score}, "error": None}


@router.get("/stats/top-vulnerabilities")
def top_vulnerabilities(db: Session = Depends(get_db)) -> dict[str, Any]:
    rows = db.query(Finding.category, func.count(Finding.id)).group_by(Finding.category).order_by(func.count(Finding.id).desc()).limit(5).all()
    return {"data": [{"category": c, "count": cnt} for c, cnt in rows], "error": None}


@router.get("/stats/developers")
def stats_developers(db: Session = Depends(get_db)) -> dict[str, Any]:
    # Placeholder aggregation per author; requires author data
    return {"data": [], "error": None}


@router.post("/findings/{finding_id}/feedback")
def submit_feedback(finding_id: str, action: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    finding = db.get(Finding, finding_id)
    if not finding:
        raise HTTPException(status_code=404, detail={"error": {"code": "NOT_FOUND", "message": "Finding not found"}})
    try:
        fb_action = FeedbackAction(action)
    except ValueError:
        raise HTTPException(status_code=400, detail={"error": {"code": "INVALID_ACTION", "message": "Use accepted|dismissed"}})
    feedback = Feedback(finding_id=finding_id, action=fb_action)
    db.add(feedback)
    db.commit()
    return {"data": {"status": "saved"}, "error": None}


@router.get("/health")
def health(db: Session = Depends(get_db)) -> dict[str, Any]:
    db_status = "ok"
    redis_status = "ok"
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001
        db_status = "error"
        log.error("db_health_check_failed", error=str(exc))
    try:
        redis.Redis.from_url(settings.REDIS_URL).ping()
    except Exception as exc:  # noqa: BLE001
        redis_status = "error"
        log.error("redis_health_check_failed", error=str(exc))
    return {"data": {"status": "ok", "db": db_status, "redis": redis_status}, "error": None}
