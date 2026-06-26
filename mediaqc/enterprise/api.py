"""Enterprise FastAPI application."""

from __future__ import annotations

from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from .auth import create_token, decode_token, has_permission, verify_password
from .config import EnterpriseSettings, load_settings
from .graphql import execute_graphql
from .models import Permission, Role, User
from .notifications import get_notification_backend
from .repositories import EnterpriseRepository, seed_repository
from .storage import get_storage_backend
from .webhooks import build_webhook_payload, sign_payload


class LoginRequest(BaseModel):
    email: str
    password: str


class UserCreate(BaseModel):
    email: str
    password: str
    role: Role = Role.VIEWER


class ProjectCreate(BaseModel):
    name: str
    workflow: str = "generic"
    metadata: dict[str, Any] = Field(default_factory=dict)


class AssetCreate(BaseModel):
    project_id: str
    filename: str
    uri: str
    storage_backend: str = "nas"
    sha256: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class WebhookCreate(BaseModel):
    url: str
    event: str
    secret: str | None = None


class NotifyRequest(BaseModel):
    channel: str
    target: str
    title: str | None = None
    message: str
    dry_run: bool = True


class GraphQLRequest(BaseModel):
    query: str


def create_enterprise_app(
    repo: EnterpriseRepository | None = None,
    settings: EnterpriseSettings | None = None,
) -> FastAPI:
    repository = repo or seed_repository()
    app_settings = settings or load_settings()
    app = FastAPI(
        title="MediaPrep Enterprise API",
        version="2.0.0",
        description="Enterprise Media Asset Management API for MediaPrep Studio.",
    )

    def current_user(authorization: str | None = Header(default=None)) -> User:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token.")
        token = authorization.removeprefix("Bearer ").strip()
        try:
            payload = decode_token(token, app_settings.secret_key)
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token.") from exc
        user = repository.get_user(payload["sub"])
        if user is None or not user.active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")
        return user

    def require(permission: Permission):
        def dependency(user: User = Depends(current_user)) -> User:
            if not has_permission(user.role, permission):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied.")
            return user

        return dependency

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "app": app_settings.app_name}

    @app.get("/overview")
    def overview(_: User = Depends(require(Permission.PROJECT_READ))) -> dict[str, Any]:
        return {
            "counts": {
                "users": len(repository.users),
                "projects": len(repository.projects),
                "assets": len(repository.assets),
                "webhooks": len(repository.webhooks),
            },
            "storage_backend": app_settings.storage_backend,
        }

    @app.get("/", response_class=HTMLResponse)
    @app.get("/dashboard", response_class=HTMLResponse)
    def dashboard() -> str:
        project_rows = "\n".join(
            f"<tr><td>{project.name}</td><td>{project.workflow}</td><td>{project.created_at}</td></tr>"
            for project in repository.projects.values()
        )
        asset_rows = "\n".join(
            f"<tr><td>{asset.filename}</td><td>{asset.storage_backend}</td><td>{asset.uri}</td></tr>"
            for asset in repository.assets.values()
        )
        return f"""
        <!doctype html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <title>MediaPrep Enterprise</title>
          <style>
            body {{ margin: 0; background: #101418; color: #e7eef7; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
            main {{ max-width: 1180px; margin: 0 auto; padding: 32px 20px; }}
            h1 {{ margin: 0 0 8px; font-size: 28px; }}
            .muted {{ color: #96a3b4; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin: 24px 0; }}
            .metric {{ border: 1px solid #25303b; background: #171d24; border-radius: 8px; padding: 16px; }}
            .metric strong {{ display: block; font-size: 30px; color: #7dd3fc; }}
            table {{ width: 100%; border-collapse: collapse; margin: 14px 0 28px; background: #141a20; }}
            th, td {{ border-bottom: 1px solid #25303b; padding: 10px 12px; text-align: left; font-size: 14px; }}
            th {{ color: #b9c6d6; background: #1b232c; }}
            code {{ color: #93c5fd; }}
          </style>
        </head>
        <body>
          <main>
            <h1>{app_settings.app_name}</h1>
            <p class="muted">Enterprise Media Asset Management dashboard foundation. OpenAPI: <code>/docs</code></p>
            <section class="grid">
              <div class="metric"><span>Users</span><strong>{len(repository.users)}</strong></div>
              <div class="metric"><span>Projects</span><strong>{len(repository.projects)}</strong></div>
              <div class="metric"><span>Assets</span><strong>{len(repository.assets)}</strong></div>
              <div class="metric"><span>Webhooks</span><strong>{len(repository.webhooks)}</strong></div>
            </section>
            <h2>Projects</h2>
            <table><thead><tr><th>Name</th><th>Workflow</th><th>Created</th></tr></thead><tbody>{project_rows or '<tr><td colspan="3">No projects yet.</td></tr>'}</tbody></table>
            <h2>Assets</h2>
            <table><thead><tr><th>Filename</th><th>Storage</th><th>URI</th></tr></thead><tbody>{asset_rows or '<tr><td colspan="3">No assets yet.</td></tr>'}</tbody></table>
          </main>
        </body>
        </html>
        """

    @app.post("/auth/login")
    def login(payload: LoginRequest) -> dict[str, Any]:
        user = repository.find_user_by_email(payload.email)
        if user is None or not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")
        return {"access_token": create_token(user, app_settings.secret_key), "token_type": "bearer", "user": user.to_public_dict()}

    @app.post("/users")
    def create_user(payload: UserCreate, _: User = Depends(require(Permission.ADMIN))) -> dict[str, Any]:
        try:
            user = repository.create_user(payload.email, payload.password, payload.role)
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        return {"user": user.to_public_dict()}

    @app.get("/users")
    def list_users(_: User = Depends(require(Permission.ADMIN))) -> dict[str, Any]:
        return {"users": [user.to_public_dict() for user in repository.users.values()]}

    @app.post("/projects")
    def create_project(payload: ProjectCreate, user: User = Depends(require(Permission.PROJECT_WRITE))) -> dict[str, Any]:
        project = repository.create_project(payload.name, user.id, payload.workflow)
        project.metadata.update(payload.metadata)
        return {"project": project.to_dict()}

    @app.get("/projects")
    def list_projects(_: User = Depends(require(Permission.PROJECT_READ))) -> dict[str, Any]:
        return {"projects": [project.to_dict() for project in repository.projects.values()]}

    @app.post("/assets")
    def create_asset(payload: AssetCreate, _: User = Depends(require(Permission.ASSET_WRITE))) -> dict[str, Any]:
        storage = get_storage_backend(payload.storage_backend).resolve(payload.uri)
        try:
            asset = repository.create_asset(payload.project_id, payload.filename, payload.uri, payload.storage_backend, payload.sha256)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        asset.metadata.update(payload.metadata)
        asset.metadata["storage_exists"] = storage.exists
        return {"asset": asset.to_dict()}

    @app.get("/assets")
    def list_assets(_: User = Depends(require(Permission.ASSET_READ))) -> dict[str, Any]:
        return {"assets": [asset.to_dict() for asset in repository.assets.values()]}

    @app.post("/webhooks")
    def create_webhook(payload: WebhookCreate, _: User = Depends(require(Permission.PROJECT_WRITE))) -> dict[str, Any]:
        webhook = repository.create_webhook(payload.url, payload.event, payload.secret)
        return {"webhook": webhook.to_dict()}

    @app.post("/webhooks/preview")
    def preview_webhook(payload: WebhookCreate, _: User = Depends(require(Permission.PROJECT_READ))) -> dict[str, Any]:
        body = build_webhook_payload(payload.event, {"preview": True})
        return {"payload": body, "signature": sign_payload(body, payload.secret or "preview")}

    @app.post("/notifications/send")
    def send_notification(payload: NotifyRequest, _: User = Depends(require(Permission.PROJECT_WRITE))) -> dict[str, Any]:
        backend = get_notification_backend(payload.channel)
        return {"notification": backend.send(payload.target, payload.message, payload.title, dry_run=payload.dry_run).__dict__}

    @app.post("/graphql")
    def graphql(payload: GraphQLRequest, _: User = Depends(require(Permission.PROJECT_READ))) -> dict[str, Any]:
        return execute_graphql(payload.query, repository)

    return app
