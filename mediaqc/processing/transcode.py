"""Transcode job creation."""

from __future__ import annotations

from pathlib import Path

from mediaqc.scanner import is_supported_media

from .encoder_backends import select_backend
from .jobs import ProcessingJob
from .presets import TranscodePreset, build_output_path, load_preset


def collect_inputs(input_path: Path, recursive: bool = False) -> list[Path]:
    path = Path(input_path)
    if path.is_file():
        return [path]
    if not path.is_dir():
        raise FileNotFoundError(f"Input path does not exist: {path}")
    iterator = path.rglob("*") if recursive else path.glob("*")
    return sorted((item for item in iterator if is_supported_media(item)), key=lambda item: str(item).casefold())


def build_transcode_jobs(
    input_path: Path,
    output_dir: Path,
    preset_name: str,
    recursive: bool = False,
    preserve_structure: bool = True,
    overwrite: bool = False,
    skip_existing: bool = False,
    backend_config: Path | None = None,
) -> list[ProcessingJob]:
    preset = load_preset(preset_name)
    inputs = collect_inputs(input_path, recursive=recursive)
    root = Path(input_path) if Path(input_path).is_dir() and preserve_structure else None
    backend = select_backend(preset, backend_config)
    jobs: list[ProcessingJob] = []
    for source in inputs:
        output_path = build_output_path(source, output_dir, preset, root=root)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        command = backend.build_command(source, output_path, preset, {"overwrite": overwrite})
        log_path = output_path.with_suffix(output_path.suffix + ".log")
        jobs.append(
            ProcessingJob(
                input_path=source,
                output_path=output_path,
                preset=preset.key,
                command=command,
                log_path=log_path,
                skip_existing=skip_existing,
            )
        )
    return jobs
