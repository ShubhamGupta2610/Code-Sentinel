"""Celery application factory."""
from __future__ import annotations

from celery import Celery
from app.core.config import settings


def create_celery_app() -> Celery:
    app = Celery(
        "codesentinel",
        broker=settings.REDIS_URL,
        backend=settings.REDIS_URL,
        include=["worker.tasks"],
    )

    app.conf.update(
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        timezone="UTC",
        task_acks_late=True,
    )

    return app


celery = create_celery_app()