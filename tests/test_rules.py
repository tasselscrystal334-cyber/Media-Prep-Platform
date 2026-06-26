from pathlib import Path

from mediaqc.models import MediaFileResult
from mediaqc.rules import ProjectRules, evaluate_rules, load_rules


def test_load_rules_from_yaml(tmp_path: Path) -> None:
    rules_path = tmp_path / "project_rules.yaml"
    rules_path.write_text(
        """
project_name: "LED Show 2026"
validators:
  audio: false
  codec: true
  resolution: true
  framerate: true
  colorspace: true
  pixfmt: true
  filesize: true
  bitrate: true
  filename: false
video:
  allowed_codecs:
    - hap
  expected_width: 3840
  expected_height: 2160
  expected_fps: 60
  allowed_pix_fmt:
    - rgb0
  expected_color_space: bt709
  min_bit_rate: 10000000
audio:
  allow_audio: false
filename:
  required_pattern: null
file:
  min_size_bytes: 10
""",
        encoding="utf-8",
    )

    rules = load_rules(rules_path)

    assert rules.project_name == "LED Show 2026"
    assert rules.video.allowed_codecs == ["hap"]
    assert rules.video.expected_fps == 60
    assert rules.video.min_bit_rate == 10000000
    assert rules.audio.allow_audio is False
    assert rules.filename.required_pattern is None
    assert rules.file.min_size_bytes == 10
    assert rules.validators["audio"] is False


def test_evaluate_rules_passes_matching_video() -> None:
    item = _media_result()
    item.ffprobe = {
        "streams": [
            {
                "codec_type": "video",
                "codec_name": "hap",
                "width": 3840,
                "height": 2160,
                "avg_frame_rate": "60/1",
                "pix_fmt": "rgb0",
                "color_space": "bt709",
            }
        ]
    }

    evaluate_rules(item, _rules())

    assert item.rule_status == "PASS"
    assert item.warnings == []
    assert item.failures == []
    assert item.validation_results


def test_evaluate_rules_fails_mismatched_video_and_audio() -> None:
    item = _media_result()
    item.ffprobe = {
        "streams": [
            {
                "codec_type": "video",
                "codec_name": "h264",
                "width": 1920,
                "height": 1080,
                "avg_frame_rate": "30/1",
                "pix_fmt": "yuv420p",
                "color_space": "bt2020nc",
            },
            {"codec_type": "audio", "codec_name": "pcm_s16le"},
        ]
    }

    evaluate_rules(item, _rules())

    assert item.rule_status == "FAIL"
    assert any("Video codec" in failure for failure in item.failures)
    assert any("Width" in failure for failure in item.failures)
    assert any("Audio stream" in failure for failure in item.failures)


def test_evaluate_rules_warns_on_file_size() -> None:
    item = _media_result(size_bytes=1)
    item.ffprobe = {
        "streams": [
            {
                "codec_type": "video",
                "codec_name": "hap",
                "width": 3840,
                "height": 2160,
                "avg_frame_rate": "60/1",
                "pix_fmt": "rgb0",
                "color_space": "bt709",
            }
        ]
    }
    rules = _rules()
    rules.file.min_size_bytes = 10

    evaluate_rules(item, rules)

    assert item.rule_status == "WARN"
    assert item.warnings
    assert item.failures == []


def test_evaluate_rules_respects_disabled_validator() -> None:
    item = _media_result()
    item.ffprobe = {
        "streams": [
            {
                "codec_type": "video",
                "codec_name": "hap",
                "width": 3840,
                "height": 2160,
                "avg_frame_rate": "60/1",
                "pix_fmt": "rgb0",
                "color_space": "bt709",
            },
            {"codec_type": "audio", "codec_name": "pcm_s16le"},
        ]
    }
    rules = _rules()
    rules.validators["audio"] = False

    evaluate_rules(item, rules)

    assert item.rule_status == "PASS"
    assert not any(result.validator == "audio" for result in item.validation_results)


def _media_result(size_bytes: int = 100) -> MediaFileResult:
    return MediaFileResult(
        path=Path("/tmp/Opening.mov"),
        filename="Opening.mov",
        extension=".mov",
        size_bytes=size_bytes,
        sha256="abc",
    )


def _rules() -> ProjectRules:
    rules = ProjectRules()
    rules.video.allowed_codecs = ["hap", "prores", "notchlc"]
    rules.video.expected_width = 3840
    rules.video.expected_height = 2160
    rules.video.expected_fps = 60
    rules.video.allowed_pix_fmt = ["rgb0", "yuv422p10le"]
    rules.video.expected_color_space = "bt709"
    rules.audio.allow_audio = False
    return rules
