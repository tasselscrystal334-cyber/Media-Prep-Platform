"""Enterprise configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(slots=True)
class EnterpriseSettings:
    app_name: str = "MediaPrep Enterprise"
    secret_key: str = "change-me"
    database_url: str = "postgresql://mediaqc:mediaqc@postgres:5432/mediaqc"
    redis_url: str = "redis://redis:6379/0"
    rabbitmq_url: str = "amqp://mediaqc:mediaqc@rabbitmq:5672//"
    minio_endpoint: str = "minio:9000"
    storage_backend: str = "nas"
    webhook_timeout_seconds: int = 5


def load_settings() -> EnterpriseSettings:
    return EnterpriseSettings(
        app_name=os.getenv("MEDIAQC_APP_NAME", "MediaPrep Enterprise"),
        secret_key=os.getenv("MEDIAQC_SECRET_KEY", "change-me"),
        database_url=os.getenv("DATABASE_URL", "postgresql://mediaqc:mediaqc@postgres:5432/mediaqc"),
        redis_url=os.getenv("REDIS_URL", "redis://redis:6379/0"),
        rabbitmq_url=os.getenv("RABBITMQ_URL", "amqp://mediaqc:mediaqc@rabbitmq:5672//"),
        minio_endpoint=os.getenv("MINIO_ENDPOINT", "minio:9000"),
        storage_backend=os.getenv("MEDIAQC_STORAGE_BACKEND", "nas"),
        webhook_timeout_seconds=int(os.getenv("MEDIAQC_WEBHOOK_TIMEOUT", "5")),
    )
