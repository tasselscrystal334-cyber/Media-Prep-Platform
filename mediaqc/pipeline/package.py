"""Project package generation for media-server workflows."""

from __future__ import annotations

import json
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

from mediaqc.live_event.manifest import build_manifest, write_manifest

SUPPORTED_WORKFLOWS = {"millumin", "disguise", "pixera", "touchdesigner", "notch"}


def build_project_package(project_path: Path, output_dir: Path, profile: str | None = None) -> dict[str, Any]:
    project = Path(project_path).resolve()
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    workflow = (profile or "generic").casefold()
    if workflow not in SUPPORTED_WORKFLOWS and workflow != "generic":
        raise ValueError(f"Unsupported package profile '{profile}'.")

    manifest = build_manifest(project, project_name=profile or project.name)
    manifest_path, manifest_csv_path = write_manifest(manifest, output)
    package_name = f"{project.name}_{workflow}_package.zip"
    package_path = output / package_name
    metadata = {
        "project_name": project.name,
        "profile": workflow,
        "generated_at": datetime.now().replace(microsecond=0).isoformat(),
        "media_count": manifest["media_count"],
        "manifest": manifest_path.name,
        "notes": _workflow_notes(workflow),
    }
    metadata_path = output / "package_metadata.json"
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    readme_path = output / "README_PROJECT_PACKAGE.txt"
    readme_path.write_text(_package_readme(metadata), encoding="utf-8")

    with zipfile.ZipFile(package_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(manifest_path, f"reports/{manifest_path.name}")
        archive.write(manifest_csv_path, f"reports/{manifest_csv_path.name}")
        archive.write(metadata_path, "package_metadata.json")
        archive.write(readme_path, "README_PROJECT_PACKAGE.txt")
        for item in manifest["files"]:
            source = project / item["relative_path"]
            if source.exists():
                archive.write(source, f"Media/{item['relative_path']}")
    return {
        "package_path": str(package_path),
        "metadata_path": str(metadata_path),
        "manifest_path": str(manifest_path),
        "media_count": manifest["media_count"],
        "profile": workflow,
    }


def _workflow_notes(workflow: str) -> list[str]:
    notes = {
        "millumin": ["Keep HAP/ProRes media paths stable before importing into Millumin."],
        "disguise": ["Import media into the show project and verify resolution/fps against stage outputs."],
        "pixera": ["Use package manifest to validate copied media on Pixera servers."],
        "touchdesigner": ["Preserve relative paths for TOE/TOP references."],
        "notch": ["Prefer NotchLC/HAP/ProRes assets and verify output with SHA256 compare."],
        "generic": ["Verify manifest and SHA256 before show playback."],
    }
    return notes.get(workflow, notes["generic"])


def _package_readme(metadata: dict[str, Any]) -> str:
    return "\n".join(
        [
            "MediaPrep Studio Project Package",
            "",
            f"Project: {metadata['project_name']}",
            f"Profile: {metadata['profile']}",
            f"Generated: {metadata['generated_at']}",
            f"Media Count: {metadata['media_count']}",
            "",
            "Contents:",
            "- Media/: packaged media files",
            "- reports/manifest.json",
            "- reports/manifest.csv",
            "- package_metadata.json",
            "",
            "Workflow Notes:",
            *[f"- {note}" for note in metadata["notes"]],
            "",
        ]
    )
