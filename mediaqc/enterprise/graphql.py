"""Minimal GraphQL entry point for V2.0 foundation."""

from __future__ import annotations

from typing import Any

from .repositories import EnterpriseRepository


def execute_graphql(query: str, repo: EnterpriseRepository) -> dict[str, Any]:
    normalized = " ".join(query.split()).casefold()
    if "projects" in normalized:
        return {"data": {"projects": [project.to_dict() for project in repo.projects.values()]}}
    if "assets" in normalized:
        return {"data": {"assets": [asset.to_dict() for asset in repo.assets.values()]}}
    if "users" in normalized:
        return {"data": {"users": [user.to_public_dict() for user in repo.users.values()]}}
    return {"errors": [{"message": "Supported root fields: users, projects, assets."}]}
