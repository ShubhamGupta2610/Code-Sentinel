"""FastAPI entrypoint for CodeSentinel."""
from __future__ import annotations

from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import (
    WebhookValidationError,
    GitHubAPIError,
    AIReviewError,
    DiffProcessingError,
    RateLimitExceededError,
)
from app.core.logger import configure_logging, get_logger
from app.webhook.github import router as webhook_router
from app.api.routes import router as api_router, health as api_health_handler
from app.db.database import get_db

configure_logging()
logger = get_logger(service="codesentinel-api")

app = FastAPI(title="CodeSentinel")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def log_startup() -> None:
    """Emit a structured startup log so observability pipelines see service boots."""
    logger.info(
        "CodeSentinel API starting",
        cors_origins="*",
        ollama_model=settings.OLLAMA_MODEL,
        log_level=settings.LOG_LEVEL,
    )


@app.exception_handler(WebhookValidationError)
async def webhook_exception_handler(request: Request, exc: WebhookValidationError):  # noqa: D401
    return JSONResponse(status_code=403, content={"error": {"code": "INVALID_SIGNATURE", "message": str(exc)}})


@app.exception_handler(GitHubAPIError)
async def github_exception_handler(request: Request, exc: GitHubAPIError):
    return JSONResponse(status_code=502, content={"error": {"code": "GITHUB_API_ERROR", "message": str(exc)}})


@app.exception_handler(AIReviewError)
async def ai_exception_handler(request: Request, exc: AIReviewError):
    return JSONResponse(status_code=500, content={"error": {"code": "AI_REVIEW_ERROR", "message": str(exc)}})


@app.exception_handler(DiffProcessingError)
async def diff_exception_handler(request: Request, exc: DiffProcessingError):
    return JSONResponse(status_code=400, content={"error": {"code": "DIFF_PROCESSING_ERROR", "message": str(exc)}})


@app.exception_handler(RateLimitExceededError)
async def rate_limit_handler(request: Request, exc: RateLimitExceededError):
    return JSONResponse(status_code=429, content={"error": {"code": "RATE_LIMIT", "message": str(exc)}})


app.include_router(webhook_router)
app.include_router(api_router, prefix="/api")


@app.get("/", tags=["health"])
@app.get("/health", tags=["health"])
async def health() -> dict[str, object]:
    """Lightweight health endpoint that doesn't hit dependencies."""
    return {"status": "ok"}


@app.get("/api/health", tags=["health"])
async def api_health(db: Session = Depends(get_db)) -> dict[str, object]:
    """Health endpoint with DB/Redis checks (alias for dashboard)."""
    return api_health_handler(db)
