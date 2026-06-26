from pathlib import Path

from mediaqc.live_event.edid import check_output_spec
from mediaqc.models import MediaFileResult


def test_output_spec_warns_for_resolution_and_fps_mismatch() -> None:
    media = MediaFileResult(Path("/tmp/opening.mov"), "opening.mov", ".mov", 1)
    media.ffprobe = {
        "streams": [
            {
                "codec_type": "video",
                "width": 3840,
                "height": 2160,
                "avg_frame_rate": "30/1",
                "color_space": "bt2020nc",
                "color_range": "tv",
            }
        ]
    }
    spec = {
        "project_name": "LED Show",
        "output": {
            "name": "Main LED",
            "target_width": 6400,
            "target_height": 2000,
            "refresh_rate": 60,
            "color_space": "bt709",
            "color_range": "full",
        },
    }

    report = check_output_spec(media, spec)

    assert report.status == "WARN"
    assert len(report.warnings) == 4
    assert report.details["media_fps"] == 30.0


def test_output_spec_passes_matching_project_spec() -> None:
    media = MediaFileResult(Path("/tmp/opening.mov"), "opening.mov", ".mov", 1)
    media.ffprobe = {
        "streams": [
            {
                "codec_type": "video",
                "width": 6400,
                "height": 2000,
                "avg_frame_rate": "60/1",
                "color_space": "bt709",
                "color_range": "pc",
            }
        ]
    }
    spec = {
        "output": {
            "target_width": 6400,
            "target_height": 2000,
            "refresh_rate": 60,
            "color_space": "bt709",
            "color_range": "full",
        },
    }

    report = check_output_spec(media, spec)

    assert report.status == "PASS"
    assert not report.warnings
