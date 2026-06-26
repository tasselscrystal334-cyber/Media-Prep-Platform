"""Logo overlay command builders."""

from __future__ import annotations

from pathlib import Path

from .presets import build_ffmpeg_args, load_preset

POSITIONS = {
    "top-left": "20:20",
    "top-right": "main_w-overlay_w-20:20",
    "bottom-left": "20:main_h-overlay_h-20",
    "bottom-right": "main_w-overlay_w-20:main_h-overlay_h-20",
    "center": "(main_w-overlay_w)/2:(main_h-overlay_h)/2",
}


def build_logo_command(
    input_path: Path,
    logo_path: Path,
    output_path: Path,
    position: str = "top-right",
    x: int | None = None,
    y: int | None = None,
    opacity: float = 1.0,
    start: float | None = None,
    end: float | None = None,
    logo_scale: float | None = None,
    preset_name: str = "h264_preview",
    overwrite: bool = False,
) -> list[str]:
    preset = load_preset(preset_name)
    base_args = build_ffmpeg_args(input_path, output_path, preset, overwrite=overwrite)
    output = base_args.pop()
    input_args_end = base_args.index("-c:v")
    args = [*base_args[:2], *base_args[2:4], "-i", str(logo_path)]
    filter_graph = _filter_graph(position, x, y, opacity, start, end, logo_scale)
    args.extend(["-filter_complex", filter_graph])
    args.extend(base_args[input_args_end:])
    args.append(output)
    return ["ffmpeg", *args[1:]]


def _filter_graph(
    position: str,
    x: int | None,
    y: int | None,
    opacity: float,
    start: float | None,
    end: float | None,
    logo_scale: float | None,
) -> str:
    coord = f"{x}:{y}" if x is not None and y is not None else POSITIONS.get(position, POSITIONS["top-right"])
    logo_chain = "[1:v]format=rgba"
    if logo_scale:
        logo_chain += f",scale=iw*{logo_scale}:ih*{logo_scale}"
    logo_chain += f",colorchannelmixer=aa={opacity}[logo]"
    overlay = f"[0:v][logo]overlay={coord}"
    if start is not None or end is not None:
        start_value = 0 if start is None else start
        end_value = 999999 if end is None else end
        overlay += f":enable='between(t,{start_value},{end_value})'"
    return f"{logo_chain};{overlay}"
