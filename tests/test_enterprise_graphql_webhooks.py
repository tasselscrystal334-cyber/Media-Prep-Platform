from mediaqc.enterprise.graphql import execute_graphql
from mediaqc.enterprise.models import Role
from mediaqc.enterprise.repositories import EnterpriseRepository
from mediaqc.enterprise.webhooks import build_webhook_payload, sign_payload


def test_graphql_root_fields() -> None:
    repo = EnterpriseRepository()
    user = repo.create_user("manager@example.com", "secret", Role.MANAGER)
    project = repo.create_project("LED Package", user.id, "pixera")
    repo.create_asset(project.id, "Opening.mov", "s3://bucket/Opening.mov", "s3", "abc")

    assert execute_graphql("{ users { email } }", repo)["data"]["users"][0]["email"] == "manager@example.com"
    assert execute_graphql("{ projects { name } }", repo)["data"]["projects"][0]["name"] == "LED Package"
    assert execute_graphql("{ assets { filename } }", repo)["data"]["assets"][0]["filename"] == "Opening.mov"
    assert "errors" in execute_graphql("{ unknown }", repo)


def test_webhook_payload_signature_is_stable() -> None:
    payload = build_webhook_payload("asset.scanned", {"asset_id": "asset-1"})
    signature = sign_payload(payload, "secret")
    assert payload["event"] == "asset.scanned"
    assert signature == sign_payload(payload, "secret")
    assert signature != sign_payload(payload, "different")
