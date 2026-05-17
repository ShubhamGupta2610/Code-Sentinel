"""Structlog-based logging setup with dev/prod modes."""
from __future__ import annotations

import logging
import os
from typing import Any

import structlog

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


def _configure_processors(json_output: bool) -> list[Any]:
    common = [
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    if json_output:
        return common + [structlog.processors.JSONRenderer()]
    return common + [structlog.dev.ConsoleRenderer()]  # type: ignore[arg-type]


def configure_logging() -> None:
    """Initialize structlog once with dev (human) vs prod (JSON) output."""
    json_output = LOG_LEVEL not in {"DEBUG", "TRACE"}
    logging.basicConfig(level=LOG_LEVEL, format="%(message)s")
    structlog.configure(
        processors=_configure_processors(json_output),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(logging.getLevelName(LOG_LEVEL)),
        cache_logger_on_first_use=True,
    )


def get_logger(**context: Any) -> structlog.stdlib.BoundLogger:
    """Return a bound logger."""
    if not structlog.is_configured():
        configure_logging()
    return structlog.get_logger().bind(**context)


# Common event names used across pipeline (for consistent logging)
EVENT = {
    "WEBHOOK_RECEIVED": "webhook_received",
    "JOB_QUEUED": "job_queued",
    "REVIEW_STARTED": "review_started",
    "LLM_CALL_STARTED": "llm_call_started",
    "LLM_RESPONSE_RECEIVED": "llm_response_received",
    "FINDINGS_PARSED": "findings_parsed",
    "JSON_PARSE_FAILED": "json_parse_failed",
    "COMMENTS_POSTED": "comments_posted",
    "REVIEW_COMPLETED": "review_completed",
    "GITHUB_API_FAILED": "github_api_failed",
    "DB_WRITE_FAILED": "db_write_failed",
    "CHUNK_TIMEOUT": "chunk_timeout",
    "CHUNK_SOFT_TIME": "chunk_soft_time_limit",
}
