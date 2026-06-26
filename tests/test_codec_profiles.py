from pathlib import Path

from mediaqc.live_event.codec_profiles import analyze_codec_profile
from mediaqc.models import MediaFileResult


def test_h264_ultrawide_is_high_risk() -> None:
    media = _media(
        {
            "codec_type": "video",
            "codec_name": "h264",
            "width": 7680,
            "height": 2160,
            "avg_frame_rate": "60/1",
            "pix_fmt": "yuv420p",
        }
    )

    profile = analyze_codec_profile(media)

    assert profile.category == "H264"
    assert profile.risk_level == "HIGH"
    assert profile.realtime_score == 20
    assert any("HIGH RISK" in item for item in profile.recommendations)


def test_notchlc_records_live_event_details() -> None:
    media = _media(
        {
            "codec_type": "video",
            "codec_name": "notchlc",
            "width": 3840,
            "height": 2160,
            "avg_frame_rate": "60/1",
            "pix_fmt": "yuv422p10le",
        },
        bit_rate="800000000",
    )

    profile = analyze_codec_profile(media)

    assert profile.category == "NotchLC"
    assert profile.risk_level == "LOW"
    assert profile.details["notchlc_record"]["bit_rate"] == "800000000"
    assert profile.details["notchlc_record"]["fps"] == 60.0


def test_hap_alpha_without_confirmed_alpha_warns() -> None:
    media = _media(
        {
            "codec_type": "video",
            "codec_name": "hap_alpha",
            "width": 1920,
            "height": 1080,
            "avg_frame_rate": "60/1",
            "pix_fmt": "rgb0",
        }
    )

    profile = analyze_codec_profile(media)

    assert profile.category == "HAP"
    assert profile.risk_level == "MEDIUM"
    assert profile.details["has_alpha"] is False
    assert any("alpha information could not be confirmed" in item for item in profile.recommendations)


def _media(video_stream: dict, bit_rate: str | None = None) -> MediaFileResult:
    media = MediaFileResult(Path("/tmp/opening.mov"), "opening.mov", ".mov", 1)
    media.ffprobe = {"streams": [video_stream]}
    if bit_rate is not None:
        media.ffprobe["bit_rate"] = bit_rate
    return media
