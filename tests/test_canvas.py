from pathlib import Path

from mediaqc.live_event.canvas import check_media_canvas, load_canvas_spec, validate_canvas_spec
from mediaqc.models import MediaFileResult


def test_validate_canvas_spec_passes_complete_layout(tmp_path: Path) -> None:
    spec_path = tmp_path / "canvas.yaml"
    spec_path.write_text(
        """
canvas:
  name: Main
  width: 6400
  height: 2000
  fps: 60
  layout:
    - name: A
      x: 0
      y: 0
      width: 3840
      height: 2000
    - name: B
      x: 3840
      y: 0
      width: 2560
      height: 2000
""",
        encoding="utf-8",
    )
    spec = load_canvas_spec(spec_path)

    report = validate_canvas_spec(spec)

    assert report.status == "PASS"
    assert report.details["coverage_percent"] == 100


def test_validate_canvas_spec_fails_overlap() -> None:
    spec = {
        "canvas": {
            "width": 6400,
            "height": 2000,
            "layout": [
                {"name": "A", "x": 0, "y": 0, "width": 4000, "height": 2000},
                {"name": "B", "x": 3000, "y": 0, "width": 3400, "height": 2000},
            ],
        }
    }

    report = validate_canvas_spec(spec)

    assert report.status == "FAIL"
    assert any("overlap" in failure for failure in report.failures)


def test_check_media_canvas_warns_resolution_mismatch() -> None:
    media = MediaFileResult(Path("/tmp/a.mov"), "a.mov", ".mov", 1)
    media.ffprobe = {"streams": [{"codec_type": "video", "width": 1920, "height": 1080}]}
    spec = {"canvas": {"width": 6400, "height": 2000}}

    report = check_media_canvas(media, spec)

    assert report.status == "WARN"
    assert report.warnings
