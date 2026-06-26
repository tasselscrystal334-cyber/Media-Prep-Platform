from pathlib import Path

from mediaqc.models import MediaFileResult
from mediaqc.profiles import load_profile, resolve_profile_path
from mediaqc.rules import evaluate_rules


def test_load_disguise_profile() -> None:
    rules, profile_path = load_profile("disguise")

    assert profile_path.name == "Disguise.yaml"
    assert rules.profile_name == "Disguise"
    assert rules.video.expected_width == 3840
    assert rules.video.expected_height == 2160
    assert rules.video.expected_fps == 60
    assert "hap" in rules.video.allowed_codecs
    assert rules.audio.allow_audio is False
    assert rules.validators["folder_structure"] is True


def test_resolve_profile_alias() -> None:
    assert resolve_profile_path("touchdesigner").name == "TouchDesigner.yaml"
    assert resolve_profile_path("led-4k").name == "LED_4K.yaml"


def test_disguise_profile_flags_non_matching_media() -> None:
    rules, _ = load_profile("disguise")
    media = MediaFileResult(
        path=Path("/tmp/random folder/中文 文件.mov"),
        filename="中文 文件.mov",
        extension=".mov",
        size_bytes=16,
        sha256="abc",
    )
    media.ffprobe = {
        "bit_rate": "5000000",
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
            {"codec_type": "audio", "codec_name": "aac"},
        ],
    }

    evaluate_rules(media, rules)

    assert media.rule_status == "FAIL"
    assert any("codec" in failure for failure in media.failures)
    assert any("resolution" in failure for failure in media.failures)
    assert any("audio" in failure for failure in media.failures)
    assert any("filename" in warning for warning in media.warnings)
    assert any("folder_structure" in warning for warning in media.warnings)
