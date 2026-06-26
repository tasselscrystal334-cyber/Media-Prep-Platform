"""Notification adapters for enterprise events."""

from __future__ import annotations

from dataclasses import dataclass
from email.message import EmailMessage
from typing import Any


@dataclass(slots=True)
class NotificationResult:
    channel: str
    target: str
    status: str
    payload: dict[str, Any]


class NotificationBackend:
    channel = "base"

    def build_payload(self, target: str, message: str, title: str | None = None) -> dict[str, Any]:
        raise NotImplementedError

    def send(self, target: str, message: str, title: str | None = None, dry_run: bool = True) -> NotificationResult:
        payload = self.build_payload(target, message, title)
        return NotificationResult(channel=self.channel, target=target, status="DRY_RUN" if dry_run else "QUEUED", payload=payload)


class SlackNotificationBackend(NotificationBackend):
    channel = "slack"

    def build_payload(self, target: str, message: str, title: str | None = None) -> dict[str, Any]:
        return {"url": target, "json": {"text": f"{title + ': ' if title else ''}{message}"}}


class TeamsNotificationBackend(NotificationBackend):
    channel = "teams"

    def build_payload(self, target: str, message: str, title: str | None = None) -> dict[str, Any]:
        return {"url": target, "json": {"title": title or "MediaPrep", "text": message}}


class FeishuNotificationBackend(NotificationBackend):
    channel = "feishu"

    def build_payload(self, target: str, message: str, title: str | None = None) -> dict[str, Any]:
        return {"url": target, "json": {"msg_type": "text", "content": {"text": f"{title or 'MediaPrep'}\n{message}"}}}


class EmailNotificationBackend(NotificationBackend):
    channel = "email"

    def build_payload(self, target: str, message: str, title: str | None = None) -> dict[str, Any]:
        email = EmailMessage()
        email["To"] = target
        email["Subject"] = title or "MediaPrep Notification"
        email.set_content(message)
        return {"message": email.as_string()}


def get_notification_backend(channel: str) -> NotificationBackend:
    backends: dict[str, NotificationBackend] = {
        "slack": SlackNotificationBackend(),
        "teams": TeamsNotificationBackend(),
        "feishu": FeishuNotificationBackend(),
        "email": EmailNotificationBackend(),
    }
    try:
        return backends[channel]
    except KeyError as exc:
        raise ValueError(f"Unknown notification channel: {channel}") from exc
