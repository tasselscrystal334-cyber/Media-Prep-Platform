"""Adobe Media Encoder watch-folder preparation for official NotchLC workflows."""

from __future__ import annotations

import csv
import json
import platform
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from mediaqc.scanner import is_supported_media

from .encoder_backends import EncoderBackend

AME_JOB_FIELDS = [
    "source_path",
    "watch_path",
    "expected_output_dir",
    "mode",
    "status",
    "note",
]

OFFICIAL_NOTCHLC_POLICY = (
    "NotchLC encoding is supported only through official Adobe Media Encoder, "
    "Adobe Premiere, Adobe After Effects, or official NotchLC SDK/tool workflows. "
    "MediaPrep Studio does not load, patch, reverse engineer, decompile, or recompile Adobe plugins."
)


@dataclass(slots=True)
class AdobeMediaEncoderBackend(EncoderBackend):
    """Prepare files for Adobe Media Encoder watch-folder encoding."""

    name: str = "adobe_media_encoder"

    def supports(self, codec_name: str) -> bool:
        return codec_name == "notchlc"

    def check_available(self) -> bool:
        return detect_adobe_media_encoder() is not None

    def build_command(self, input_path: Path, output_path: Path, preset: Any, options: dict[str, Any] | None = None) -> list[str]:
        raise NotImplementedError(
            "AdobeMediaEncoderBackend does not directly invoke Adobe plugins. Use mediaqc notchlc prepare."
        )

    def plugin_may_be_available(self) -> bool:
        return detect_notchlc_adobe_plugin_hint()


def detect_adobe_media_encoder() -> Path | None:
    """Return a likely Adobe Media Encoder application path when discoverable."""

    system = platform.system()
    candidates: list[Path] = []
    if system == "Darwin":
        candidates.extend(sorted(Path("/Applications").glob("Adobe Media Encoder */Adobe Media Encoder *.app")))
        candidates.append(Path("/Applications/Adobe Media Encoder.app"))
    elif system == "Windows":
        program_files = [Path("C:/Program Files"), Path("C:/Program Files/Adobe")]
        for base in program_files:
            candidates.extend(base.glob("Adobe/Adobe Media Encoder */Adobe Media Encoder.exe"))
            candidates.extend(base.glob("Adobe Media Encoder */Adobe Media Encoder.exe"))
    else:
        executable = shutil.which("Adobe Media Encoder") or shutil.which("ame")
        if executable:
            candidates.append(Path(executable))
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def detect_notchlc_adobe_plugin_hint() -> bool:
    """Best-effort plugin hint without loading or inspecting plugin binaries."""

    home = Path.home()
    candidates = [
        Path("/Library/Application Support/Adobe/Common/Plug-ins"),
        home / "Library/Application Support/Adobe/Common/Plug-ins",
        Path("C:/Program Files/Adobe/Common/Plug-ins"),
    ]
    for base in candidates:
        if not base.exists():
            continue
        try:
            if any("notch" in path.name.casefold() for path in base.rglob("*")):
                return True
        except OSError:
            continue
    return False


def prepare_ame_notchlc_jobs(
    input_path: Path,
    watch_folder: Path,
    output_dir: Path,
    recursive: bool = False,
    link: bool = False,
) -> dict[str, Any]:
    """Copy or link inputs into an AME watch folder and write AME job manifests."""

    sources = _collect_sources(input_path, recursive)
    watch = Path(watch_folder)
    output = Path(output_dir)
    watch.mkdir(parents=True, exist_ok=True)
    output.mkdir(parents=True, exist_ok=True)

    jobs: list[dict[str, Any]] = []
    root = Path(input_path).resolve() if Path(input_path).is_dir() else Path(input_path).resolve().parent
    for source in sources:
        relative = _safe_relative(source.resolve(), root)
        watch_path = watch / relative
        watch_path.parent.mkdir(parents=True, exist_ok=True)
        status = "READY"
        note = "Copied to AME watch folder."
        try:
            if link:
                if watch_path.exists():
                    watch_path.unlink()
                watch_path.symlink_to(source.resolve())
                note = "Linked to AME watch folder."
            else:
                shutil.copy2(source, watch_path)
        except OSError as exc:
            status = "FAILED"
            note = str(exc)
        jobs.append(
            {
                "source_path": str(source.resolve()),
                "watch_path": str(watch_path),
                "expected_output_dir": str(output.resolve()),
                "mode": "link" if link else "copy",
                "status": status,
                "note": note,
            }
        )

    payload = {
        "generated_at": datetime.now().replace(microsecond=0).isoformat(),
        "policy": OFFICIAL_NOTCHLC_POLICY,
        "adobe_media_encoder_path": str(detect_adobe_media_encoder()) if detect_adobe_media_encoder() else None,
        "notchlc_adobe_plugin_hint": detect_notchlc_adobe_plugin_hint(),
        "watch_folder": str(watch.resolve()),
        "output_dir": str(output.resolve()),
        "total_jobs": len(jobs),
        "jobs": jobs,
    }
    _write_ame_reports(payload, watch)
    return payload


def write_ame_readme(watch_folder: Path, output_dir: Path) -> Path:
    path = Path(watch_folder) / "README_AME_NOTCHLC.txt"
    path.write_text(
        "\n".join(
            [
                "MediaPrep Studio - Adobe Media Encoder NotchLC Watch Folder",
                "",
                OFFICIAL_NOTCHLC_POLICY,
                "",
                "Instructions:",
                "1. Open Adobe Media Encoder.",
                "2. Add this folder as an AME Watch Folder.",
                "3. Choose an official NotchLC preset provided by the legal Adobe plugin or official toolchain.",
                f"4. Set the output folder to: {Path(output_dir).resolve()}",
                "5. Start the AME queue and wait for encoded files to appear.",
                "6. Run MediaPrep Studio QC, ffprobe, SHA256, and manifest generation on the output folder.",
                "",
                "This workflow does not call, load, inspect, patch, reverse engineer, decompile, or recompile any Adobe plugin binary.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def _write_ame_reports(payload: dict[str, Any], watch_folder: Path) -> tuple[Path, Path, Path]:
    watch = Path(watch_folder)
    json_path = watch / "ame_jobs.json"
    csv_path = watch / "ame_jobs.csv"
    readme_path = write_ame_readme(watch, Path(payload["output_dir"]))
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8-sig") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=AME_JOB_FIELDS)
        writer.writeheader()
        for job in payload["jobs"]:
            writer.writerow({field: job.get(field, "") for field in AME_JOB_FIELDS})
    return json_path, csv_path, readme_path


def _collect_sources(input_path: Path, recursive: bool) -> list[Path]:
    path = Path(input_path)
    if path.is_file():
        return [path]
    iterator = path.rglob("*") if recursive else path.glob("*")
    return sorted((item for item in iterator if is_supported_media(item)), key=lambda item: str(item).casefold())


def _safe_relative(path: Path, root: Path) -> Path:
    try:
        return path.relative_to(root)
    except ValueError:
        return Path(path.name)
