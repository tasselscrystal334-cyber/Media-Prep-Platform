"""Network target helpers for mounted NAS workflows."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


SUPPORTED_PROTOCOLS = {"local", "smb", "afp", "nfs"}


@dataclass(slots=True)
class NetworkTarget:
    raw: str
    protocol: str
    path: Path
    mounted: bool
    writable: bool
    warnings: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "raw": self.raw,
            "protocol": self.protocol,
            "path": str(self.path),
            "mounted": self.mounted,
            "writable": self.writable,
            "warnings": self.warnings,
        }


def resolve_network_target(destination: str | Path) -> NetworkTarget:
    raw = str(destination)
    parsed = urlparse(raw)
    warnings: list[str] = []
    protocol = "local"
    if parsed.scheme:
        protocol = parsed.scheme.casefold()
        if protocol not in SUPPORTED_PROTOCOLS:
            warnings.append(f"Unsupported protocol '{protocol}'. Treating destination as a local path.")
            protocol = "local"
        if protocol in {"smb", "afp", "nfs"}:
            warnings.append(
                f"{protocol.upper()} destinations must be mounted by the operating system before syncing."
            )
            path = Path(parsed.path or raw)
        else:
            path = Path(parsed.path or raw)
    else:
        path = Path(raw)
    path = path.expanduser()
    mounted = path.exists()
    writable = mounted and path.is_dir()
    if mounted and writable:
        try:
            probe = path / ".mediaqc_write_test"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink()
        except OSError:
            writable = False
            warnings.append(f"Destination is not writable: {path}")
    elif not mounted:
        warnings.append(f"Destination path does not exist yet: {path}")
    return NetworkTarget(raw=raw, protocol=protocol, path=path, mounted=mounted, writable=writable, warnings=warnings)
