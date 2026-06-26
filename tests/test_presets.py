from pathlib import Path

import pytest

from mediaqc.processing.encoder_backends import select_backend
from mediaqc.processing.ffmpeg_runner import EncoderNotAvailableError
from mediaqc.processing.overlay import build_logo_command
from mediaqc.processing.presets import build_ffmpeg_args, build_output_path, load_preset
from mediaqc.processing.subtitles import build_subtitle_command


def test_preset_parsing_and_ffmpeg_command_generation() -> None:
    preset = load_preset("h264_preview")
    output_path = build_output_path(Path("Media/Opening.mov"), Path("encoded"), preset)
    args = build_ffmpeg_args(Path("Media/Opening.mov"), output_path, preset, overwrite=True)

    assert preset.video_codec == "libx264"
    assert output_path == Path("encoded/Opening_preview.mp4")
    assert "-c:v" in args
    assert "libx264" in args
    assert args[-1] == "encoded/Opening_preview.mp4"


def test_subtitle_soft_and_burn_command_generation() -> None:
    soft = build_subtitle_command(Path("input.mov"), Path("captions.srt"), Path("output.mp4"), "soft")
    burn = build_subtitle_command(
        Path("input.mov"),
        Path("captions.ass"),
        Path("output.mp4"),
        "burn",
        fonts_dir=Path("fonts"),
    )

    assert soft[:3] == ["ffmpeg", "-n", "-i"]
    assert "mov_text" in soft
    assert "-vf" in burn
    assert any("subtitles=" in item for item in burn)
    assert any("fontsdir" in item for item in burn)


def test_logo_overlay_command_generation() -> None:
    command = build_logo_command(
        Path("input.mov"),
        Path("logo.png"),
        Path("output.mp4"),
        position="bottom-right",
        opacity=0.8,
        start=5,
        end=20,
        overwrite=True,
    )

    assert command[0] == "ffmpeg"
    assert "-filter_complex" in command
    filter_graph = command[command.index("-filter_complex") + 1]
    assert "overlay=main_w-overlay_w-20:main_h-overlay_h-20" in filter_graph
    assert "colorchannelmixer=aa=0.8" in filter_graph
    assert "between(t,5,20)" in filter_graph


def test_notchlc_backend_unavailable_has_clear_error() -> None:
    preset = load_preset("notchlc")

    with pytest.raises(EncoderNotAvailableError, match="NotchLC encoder backend is not available"):
        select_backend(preset)
