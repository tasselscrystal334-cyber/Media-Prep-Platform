"""Celery worker entry point."""

from __future__ import annotations

from .tasks import create_celery_app


def main() -> None:
    app = create_celery_app()
    app.worker_main(["worker", "--loglevel=INFO"])


if __name__ == "__main__":
    main()
