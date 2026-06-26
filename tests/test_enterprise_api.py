from pathlib import Path

from fastapi.testclient import TestClient

from mediaqc.enterprise.api import create_enterprise_app
from mediaqc.enterprise.config import EnterpriseSettings


def login(client: TestClient) -> str:
    response = client.post("/auth/login", json={"email": "admin@example.com", "password": "admin"})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_enterprise_rest_project_asset_graphql_flow(tmp_path: Path) -> None:
    app = create_enterprise_app(settings=EnterpriseSettings(secret_key="test-secret"))
    client = TestClient(app)

    assert client.get("/health").json()["status"] == "ok"

    token = login(client)
    headers = {"Authorization": f"Bearer {token}"}

    dashboard = client.get("/dashboard")
    assert dashboard.status_code == 200
    assert "Enterprise Media Asset Management" in dashboard.text

    project_response = client.post(
        "/projects",
        headers=headers,
        json={"name": "Disguise Server Prep", "workflow": "disguise", "metadata": {"venue": "arena"}},
    )
    assert project_response.status_code == 200
    project = project_response.json()["project"]

    media_file = tmp_path / "Opening.mov"
    media_file.write_bytes(b"media")
    asset_response = client.post(
        "/assets",
        headers=headers,
        json={
            "project_id": project["id"],
            "filename": media_file.name,
            "uri": str(media_file),
            "storage_backend": "nas",
            "sha256": "abc",
        },
    )
    assert asset_response.status_code == 200
    asset = asset_response.json()["asset"]
    assert asset["metadata"]["storage_exists"] is True

    graphql_response = client.post("/graphql", headers=headers, json={"query": "{ projects { id name } }"})
    assert graphql_response.status_code == 200
    assert graphql_response.json()["data"]["projects"][0]["name"] == "Disguise Server Prep"

    overview_response = client.get("/overview", headers=headers)
    assert overview_response.status_code == 200
    assert overview_response.json()["counts"]["projects"] == 1
    assert overview_response.json()["counts"]["assets"] == 1


def test_enterprise_api_rejects_missing_token() -> None:
    client = TestClient(create_enterprise_app())
    response = client.get("/projects")
    assert response.status_code == 401
