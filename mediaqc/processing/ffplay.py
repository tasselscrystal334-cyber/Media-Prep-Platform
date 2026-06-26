"""FFplay preview command builder."""

from __future__ import annotations

from pathlib import Path

from .ffmpeg_runner import CommandResult, run_ffplay


def build_ffplay_args(
    input_path: Path,
    loop: bool = False,
    mute: bool = False,
    start: str | None = None,
    scale: float | None = None,
    timecode: bool = False,
) -> list[str]:
    args: list[str] = []
    if loop:
        args.extend(["-loop", "0"])
    if mute:
        args.append("-an")
    if start:
        args.extend(["-ss", str(start)])
    if scale:
        args.extend(["-vf", f"scale=iw*{scale}:ih*{scale}"])
    if timecode:
        args.extend(["-vf", _merge_vf(args, "drawtext=text='%{pts\\:hms}':x=20:y=20:fontsize=28:fontcolor=white:box=1")])
    args.append(str(Path(input_path)))
    return _dedupe_vf(args)


def play_media(
    input_path: Path,
    loop: bool = False,
    mute: bool = False,
    start: str | None = None,
    scale: float | None = None,
    timecode: bool = False,
    dry_run: bool = False,
) -> CommandResult:
    return run_ffplay(build_ffplay_args(input_path, loop, mute, start, scale, timecode), dry_run=dry_run)


def _merge_vf(args: list[str], filter_expr: str) -> str:
    if "-vf" not in args:
        return filter_expr
    index = args.index("-vf") + 1
    return f"{args[index]},{filter_expr}"


def _dedupe_vf(args: list[str]) -> list[str]:
    if args.count("-vf") <= 1:
        return args
    output: list[str] = []
    last_filter = None
    skip_next = False
    for index, item in enumerate(args):
        if skip_next:
            skip_next = False
            continue
        if item == "-vf":
            last_filter = args[index + 1]
            skip_next = True
            continue
        output.append(item)
    if last_filter:
        insert_at = max(0, len(output) - 1)
        output[insert_at:insert_at] = ["-vf", last_filter]
    return output
