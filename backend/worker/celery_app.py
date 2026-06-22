from celery import Celery
from app.core.config import settings
import ssl

def create_celery_app() -> Celery:
    app = Celery(
        "codesentinel",
        broker=settings.CELERY_REDIS_URL,
        backend=settings.CELERY_REDIS_URL,
        include=["worker.tasks"],
    )

    app.conf.update(
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        timezone="UTC",
        task_acks_late=True,


        broker_use_ssl={
            "ssl_cert_reqs": ssl.CERT_REQUIRED,
        },

        redis_backend_use_ssl={
            "ssl_cert_reqs": ssl.CERT_REQUIRED,
        },
    )

    return app


celery = create_celery_app()