"""Webhook payload and signature helpers."""

from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any


def build_webhook_payload(event: str, data: dict[str, Any]) -> dict[str, Any]:
    return {"event": event, "data": data}


def sign_payload(payload: dict[str, Any], secret: str) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
