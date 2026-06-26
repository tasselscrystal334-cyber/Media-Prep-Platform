"""Token auth and permissions for enterprise API."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
from typing import Any

from .models import Permission, Role, ROLE_PERMISSIONS, User


def hash_password(password: str, salt: str = "mediaqc") -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000).hex()


def verify_password(password: str, password_hash: str) -> bool:
    return hmac.compare_digest(hash_password(password), password_hash)


def create_token(user: User, secret_key: str) -> str:
    payload = {"sub": user.id, "email": user.email, "role": user.role.value}
    payload_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    payload_b64 = base64.urlsafe_b64encode(payload_bytes).decode("ascii").rstrip("=")
    signature = hmac.new(secret_key.encode(), payload_b64.encode(), hashlib.sha256).hexdigest()
    return f"{payload_b64}.{signature}"


def decode_token(token: str, secret_key: str) -> dict[str, Any]:
    payload_b64, signature = token.split(".", 1)
    expected = hmac.new(secret_key.encode(), payload_b64.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected):
        raise ValueError("Invalid token signature.")
    padded = payload_b64 + "=" * (-len(payload_b64) % 4)
    return json.loads(base64.urlsafe_b64decode(padded.encode("ascii")))


def has_permission(role: Role | str, permission: Permission | str) -> bool:
    role_value = Role(role)
    permission_value = Permission(permission)
    return Permission.ADMIN in ROLE_PERMISSIONS[role_value] or permission_value in ROLE_PERMISSIONS[role_value]
