"""Enterprise domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4


def now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


class Role(StrEnum):
    ADMIN = "admin"
    MANAGER = "manager"
    OPERATOR = "operator"
    VIEWER = "viewer"


class Permission(StrEnum):
    PROJECT_READ = "project:read"
    PROJECT_WRITE = "project:write"
    ASSET_READ = "asset:read"
    ASSET_WRITE = "asset:write"
    ADMIN = "admin"


ROLE_PERMISSIONS = {
    Role.ADMIN: {Permission.ADMIN, Permission.PROJECT_READ, Permission.PROJECT_WRITE, Permission.ASSET_READ, Permission.ASSET_WRITE},
    Role.MANAGER: {Permission.PROJECT_READ, Permission.PROJECT_WRITE, Permission.ASSET_READ, Permission.ASSET_WRITE},
    Role.OPERATOR: {Permission.PROJECT_READ, Permission.ASSET_READ, Permission.ASSET_WRITE},
    Role.VIEWER: {Permission.PROJECT_READ, Permission.ASSET_READ},
}


@dataclass(slots=True)
class User:
    email: str
    password_hash: str
    role: Role = Role.VIEWER
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=now_iso)
    active: bool = True

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "email": self.email,
            "role": self.role.value,
            "created_at": self.created_at,
            "active": self.active,
        }


@dataclass(slots=True)
class Project:
    name: str
    owner_id: str
    workflow: str = "generic"
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=now_iso)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "owner_id": self.owner_id,
            "workflow": self.workflow,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }


@dataclass(slots=True)
class Asset:
    project_id: str
    filename: str
    uri: str
    storage_backend: str = "nas"
    sha256: str | None = None
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=now_iso)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "filename": self.filename,
            "uri": self.uri,
            "storage_backend": self.storage_backend,
            "sha256": self.sha256,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }


@dataclass(slots=True)
class Webhook:
    url: str
    event: str
    secret: str | None = None
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=now_iso)

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "url": self.url, "event": self.event, "created_at": self.created_at}
