"""Create release assets, checksums, and notes for MediaQC builds."""

from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
import sys
import zipfile
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    args = parse_args()
    dist_dir = Path(args.dist).resolve()
    output_dir = Path(args.output).resolve()
    version = read_version()

    output_dir.mkdir(parents=True, exist_ok=True)
    assets = []
    for bundle_name in ("mediaqc-cli", "mediaqc-gui"):
        bundle_path = dist_dir / bundle_name
        if bundle_path.exists():
            archive = output_dir / f"{bundle_name}-{version}-{args.platform}.zip"
            zip_directory(bundle_path, archive)
            assets.append(archive)

    dockerfile = ROOT / "packaging" / "docker" / "Dockerfile"
    if dockerfile.exists():
        docker_context = output_dir / f"mediaqc-docker-{version}"
        if docker_context.exists():
            shutil.rmtree(docker_context)
        docker_context.mkdir(parents=True)
        shutil.copy2(dockerfile, docker_context / "Dockerfile")
        shutil.copy2(ROOT / "packaging" / "docker" / "docker-compose.yml", docker_context / "docker-compose.yml")
        archive = output_dir / f"mediaqc-docker-{version}-{args.platform}.zip"
        zip_directory(docker_context, archive)
        assets.append(archive)

    checksum_file = output_dir / "SHA256SUMS.txt"
    write_checksums(assets, checksum_file)
    write_release_notes(output_dir / "release_notes.md", version, args.platform, assets)
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build release asset metadata.")
    parser.add_argument("--platform", required=True, help="Release platform label, e.g. windows, macos, linux.")
    parser.add_argument("--dist", default="dist", help="PyInstaller dist directory.")
    parser.add_argument("--output", default="dist_release", help="Release asset output directory.")
    return parser.parse_args()


def read_version() -> str:
    namespace: dict[str, str] = {}
    init_file = ROOT / "mediaqc" / "__init__.py"
    exec(init_file.read_text(encoding="utf-8"), namespace)
    return namespace.get("__version__", "0.0.0")


def zip_directory(source: Path, destination: Path) -> None:
    if destination.exists():
        destination.unlink()
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in source.rglob("*"):
            if path.is_file():
                archive.write(path, path.relative_to(source.parent))


def write_checksums(assets: list[Path], destination: Path) -> None:
    lines = []
    for asset in sorted(assets, key=lambda item: item.name):
        digest = hashlib.sha256(asset.read_bytes()).hexdigest()
        lines.append(f"{digest}  {asset.name}")
    destination.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def write_release_notes(destination: Path, version: str, platform: str, assets: list[Path]) -> None:
    commit = current_commit()
    generated_at = datetime.now(UTC).replace(microsecond=0).isoformat()
    asset_lines = "\n".join(f"- `{asset.name}`" for asset in sorted(assets, key=lambda item: item.name)) or "- No binary assets found."
    destination.write_text(
        "\n".join(
            [
                f"# MediaQC {version} Release",
                "",
                f"- Platform: `{platform}`",
                f"- Generated at: `{generated_at}`",
                f"- Commit: `{commit}`",
                "",
                "## Assets",
                "",
                asset_lines,
                "",
                "## Notes",
                "",
                "- CLI entry: `mediaqc`.",
                "- GUI entry: `mediaqc-gui`.",
                "- FFmpeg tools can be external via PATH or bundled in a `tools/` folder beside the executable.",
                "- Verify downloads with `SHA256SUMS.txt`.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def current_commit() -> str:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return "unknown"
    return completed.stdout.strip() or "unknown"


if __name__ == "__main__":
    raise SystemExit(main())
