"""Celery task placeholders for enterprise workers."""

from __future__ import annotations

from typing import Any


def create_celery_app() -> Any:
    try:
        from celery import Celery
    except ImportError as exc:
        raise RuntimeError("Celery is not installed. Install enterprise dependencies to run workers.") from exc

    from .config import load_settings

    settings = load_settings()
    return Celery("mediaqc", broker=settings.rabbitmq_url, backend=settings.redis_url)
