"""FastAPI dashboard for Loom."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .database import MediaDatabase
from .branding import PRODUCT_NAME


def create_app(database_path: Path = Path("./reports/media.db")) -> FastAPI:
    app = FastAPI(
        title=f"{PRODUCT_NAME} Dashboard",
        version="0.9.0",
        description=f"Dashboard and REST API for {PRODUCT_NAME} SQLite reports.",
    )
    templates = Jinja2Templates(directory=str(Path(__file__).parent / "dashboard_templates"))
    db_path = Path(database_path)

    def read_db() -> MediaDatabase:
        return MediaDatabase(db_path)

    def context(request: Request, page: str, **extra: Any) -> dict[str, Any]:
        data = {
            "request": request,
            "page": page,
            "database_path": str(db_path),
        }
        data.update(extra)
        return data

    @app.get("/", response_class=HTMLResponse)
    def overview_page(request: Request) -> HTMLResponse:
        with read_db() as db:
            overview = db.overview()
            stats = db.statistics()
        return templates.TemplateResponse(
            request,
            "overview.html",
            context(request, "overview", overview=overview, stats=stats),
        )

    @app.get("/projects", response_class=HTMLResponse)
    def projects_page(request: Request) -> HTMLResponse:
        with read_db() as db:
            projects = [dict(row) for row in db.projects()]
        return templates.TemplateResponse(
            request,
            "projects.html",
            context(request, "projects", projects=projects),
        )

    @app.get("/history", response_class=HTMLResponse)
    def history_page(request: Request) -> HTMLResponse:
        with read_db() as db:
            history = [dict(row) for row in db.history(50)]
        return templates.TemplateResponse(
            request,
            "history.html",
            context(request, "history", history=history),
        )

    @app.get("/files", response_class=HTMLResponse)
    def files_page(
        request: Request,
        q: str | None = Query(default=None),
    ) -> HTMLResponse:
        with read_db() as db:
            files = [dict(row) for row in db.media_files(q, 300)]
        return templates.TemplateResponse(
            request,
            "files.html",
            context(request, "files", files=files, query=q or ""),
        )

    @app.get("/search", response_class=HTMLResponse)
    def search_page(
        request: Request,
        q: str | None = Query(default=None),
    ) -> HTMLResponse:
        with read_db() as db:
            files = [dict(row) for row in db.media_files(q, 300)] if q else []
        template = "_files_table.html" if request.headers.get("hx-request") else "search.html"
        return templates.TemplateResponse(
            request,
            template,
            context(request, "search", files=files, query=q or ""),
        )

    @app.get("/statistics", response_class=HTMLResponse)
    def statistics_page(request: Request) -> HTMLResponse:
        with read_db() as db:
            stats = db.statistics()
        return templates.TemplateResponse(
            request,
            "statistics.html",
            context(request, "statistics", stats=stats),
        )

    @app.get("/duplicates", response_class=HTMLResponse)
    def duplicates_page(request: Request) -> HTMLResponse:
        with read_db() as db:
            duplicates = [dict(row) for row in db.duplicates()]
        return templates.TemplateResponse(
            request,
            "duplicates.html",
            context(request, "duplicates", duplicates=duplicates),
        )

    @app.get("/api/overview")
    def api_overview() -> dict[str, Any]:
        with read_db() as db:
            return db.overview()

    @app.get("/api/projects")
    def api_projects() -> dict[str, Any]:
        with read_db() as db:
            return {"projects": [dict(row) for row in db.projects()]}

    @app.get("/api/history")
    def api_history(limit: int = Query(default=50, ge=1, le=500)) -> dict[str, Any]:
        with read_db() as db:
            return {"history": [dict(row) for row in db.history(limit)]}

    @app.get("/api/files")
    def api_files(
        q: str | None = Query(default=None),
        limit: int = Query(default=200, ge=1, le=1000),
    ) -> dict[str, Any]:
        with read_db() as db:
            return {"files": [dict(row) for row in db.media_files(q, limit)]}

    @app.get("/api/search")
    def api_search(q: str = Query(default="")) -> dict[str, Any]:
        with read_db() as db:
            return {"query": q, "files": [dict(row) for row in db.media_files(q, 300)]}

    @app.get("/api/statistics")
    def api_statistics() -> dict[str, Any]:
        with read_db() as db:
            return db.statistics()

    @app.get("/api/duplicates")
    def api_duplicates() -> dict[str, Any]:
        with read_db() as db:
            return {"duplicates": [dict(row) for row in db.duplicates()]}

    return app
