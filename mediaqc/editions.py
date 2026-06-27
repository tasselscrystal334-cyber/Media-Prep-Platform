"""Product edition and licensing metadata."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EditionInfo:
    """Human-readable product edition metadata."""

    name: str
    license_name: str
    features: tuple[str, ...]


COMMUNITY_EDITION = EditionInfo(
    name="Community Edition",
    license_name="Apache License 2.0",
    features=(
        "FFmpeg integration",
        "FFprobe metadata",
        "SHA256 verification",
        "Media validation",
        "Batch transcoding",
    ),
)

ENTERPRISE_EDITION = EditionInfo(
    name="Enterprise Edition",
    license_name="Commercial License",
    features=(
        "Multi-user permissions",
        "LDAP/AD integration",
        "Audit logs",
        "NAS cluster workflows",
        "Web management dashboard",
        "Automatic content distribution",
        "Render Farm management",
    ),
)


def get_edition_matrix() -> tuple[EditionInfo, EditionInfo]:
    """Return the supported product editions in display order."""

    return COMMUNITY_EDITION, ENTERPRISE_EDITION
