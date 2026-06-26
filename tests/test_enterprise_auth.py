from mediaqc.enterprise.auth import create_token, decode_token, has_permission, hash_password, verify_password
from mediaqc.enterprise.models import Permission, Role
from mediaqc.enterprise.repositories import seed_repository


def test_password_hash_and_token_roundtrip() -> None:
    repo = seed_repository()
    user = repo.find_user_by_email("admin@example.com")
    assert user is not None

    password_hash = hash_password("admin")
    assert verify_password("admin", password_hash)
    assert not verify_password("wrong", password_hash)

    token = create_token(user, "secret")
    payload = decode_token(token, "secret")
    assert payload["sub"] == user.id
    assert payload["email"] == "admin@example.com"
    assert payload["role"] == Role.ADMIN.value


def test_role_permissions() -> None:
    assert has_permission(Role.ADMIN, Permission.ADMIN)
    assert has_permission(Role.MANAGER, Permission.ASSET_WRITE)
    assert has_permission(Role.OPERATOR, Permission.ASSET_WRITE)
    assert not has_permission(Role.OPERATOR, Permission.PROJECT_WRITE)
    assert has_permission(Role.VIEWER, Permission.ASSET_READ)
    assert not has_permission(Role.VIEWER, Permission.ASSET_WRITE)
