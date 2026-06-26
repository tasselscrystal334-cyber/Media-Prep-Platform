"""In-memory enterprise repositories for V2.0 reference implementation."""

from __future__ import annotations

from dataclasses import dataclass, field

from .auth import hash_password
from .models import Asset, Project, Role, User, Webhook


@dataclass(slots=True)
class EnterpriseRepository:
    users: dict[str, User] = field(default_factory=dict)
    projects: dict[str, Project] = field(default_factory=dict)
    assets: dict[str, Asset] = field(default_factory=dict)
    webhooks: dict[str, Webhook] = field(default_factory=dict)

    def create_user(self, email: str, password: str, role: Role = Role.VIEWER) -> User:
        if any(user.email == email for user in self.users.values()):
            raise ValueError("User already exists.")
        user = User(email=email, password_hash=hash_password(password), role=role)
        self.users[user.id] = user
        return user

    def find_user_by_email(self, email: str) -> User | None:
        for user in self.users.values():
            if user.email == email:
                return user
        return None

    def get_user(self, user_id: str) -> User | None:
        return self.users.get(user_id)

    def create_project(self, name: str, owner_id: str, workflow: str = "generic") -> Project:
        project = Project(name=name, owner_id=owner_id, workflow=workflow)
        self.projects[project.id] = project
        return project

    def create_asset(self, project_id: str, filename: str, uri: str, storage_backend: str = "nas", sha256: str | None = None) -> Asset:
        if project_id not in self.projects:
            raise ValueError("Project does not exist.")
        asset = Asset(project_id=project_id, filename=filename, uri=uri, storage_backend=storage_backend, sha256=sha256)
        self.assets[asset.id] = asset
        return asset

    def create_webhook(self, url: str, event: str, secret: str | None = None) -> Webhook:
        webhook = Webhook(url=url, event=event, secret=secret)
        self.webhooks[webhook.id] = webhook
        return webhook


def seed_repository() -> EnterpriseRepository:
    repo = EnterpriseRepository()
    repo.create_user("admin@example.com", "admin", Role.ADMIN)
    return repo
