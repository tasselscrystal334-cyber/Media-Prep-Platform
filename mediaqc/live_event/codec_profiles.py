"""Live event codec profile analysis."""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any


@dataclass(slots=True)
class CodecProfile:
    category: str = "Other"
    realtime_score: int = 50
    risk_level: str = "MEDIUM"
    recommendations: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self.category,
            "realtime_score": self.realtime_score,
            "risk_level": self.risk_level,
            "recommendations": self.recommendations,
            "details": self.details,
        }


def analyze_codec_profile(media: Any) -> CodecProfile:
    video = _video_stream(media)
    if not video:
        return CodecProfile(category="Other", realtime_score=0, risk_level="HIGH", recommendations=["No video stream found."])

    codec = str(video.get("codec_name") or "").casefold()
    pix_fmt = str(video.get("pix_fmt") or "").casefold()
    width = int(video.get("width") or 0)
    height = int(video.get("height") or 0)
    fps = _fps(video.get("avg_frame_rate"))
    bit_rate = (getattr(media, "ffprobe", None) or {}).get("bit_rate")
    has_alpha = _has_alpha(codec, pix_fmt)
    category = _category(codec)
    profile = CodecProfile(
        category=category,
        details={
            "codec_name": codec,
            "pix_fmt": pix_fmt,
            "width": width,
            "height": height,
            "fps": fps,
            "bit_rate": bit_rate,
            "has_alpha": has_alpha,
        },
    )

    pixels = width * height
    ultra_wide = width >= 7680 or pixels >= 7680 * 2160
    alpha_hint = has_alpha or "alpha" in codec or "4444" in codec

    if category in {"HAP", "NotchLC", "ProRes"}:
        profile.realtime_score = 90
        profile.risk_level = "LOW"
    elif category in {"H264", "HEVC"}:
        profile.realtime_score = 45
        profile.risk_level = "MEDIUM"
        profile.recommendations.append("H264/HEVC can be risky for large real-time playback canvases.")
    else:
        profile.realtime_score = 55
        profile.risk_level = "MEDIUM"
        profile.recommendations.append("Use HAP, ProRes, or NotchLC for predictable live playback.")

    if codec.startswith("hap") and pix_fmt not in {"rgb0", "rgba", "hap", ""}:
        profile.recommendations.append("HAP素材推荐 pix_fmt 为 rgb0 / rgba / hap.")
        profile.risk_level = _max_risk(profile.risk_level, "MEDIUM")
        profile.realtime_score = min(profile.realtime_score, 75)

    if "alpha" in codec and not has_alpha:
        profile.recommendations.append("Alpha codec name detected, but alpha information could not be confirmed.")
        profile.risk_level = _max_risk(profile.risk_level, "MEDIUM")

    if alpha_hint and not any(token in codec for token in ("hap_alpha", "hap_q_alpha", "prores")):
        profile.recommendations.append("Transparent media is usually safer as hap_alpha, hap_q_alpha, or ProRes 4444.")

    if ultra_wide and category in {"H264", "HEVC"}:
        profile.risk_level = "HIGH"
        profile.realtime_score = 20
        profile.recommendations.append("8K or ultra-wide H264/HEVC is HIGH RISK for real-time playback.")
    elif ultra_wide and codec not in {"hap_q", "notchlc", "prores"} and not codec.startswith("prores"):
        profile.recommendations.append("8K/ultra-wide canvases are best delivered as hap_q, NotchLC, or ProRes.")
        profile.risk_level = _max_risk(profile.risk_level, "MEDIUM")

    if category == "NotchLC":
        profile.details["notchlc_record"] = {
            "codec_name": codec,
            "pix_fmt": pix_fmt,
            "width": width,
            "height": height,
            "fps": fps,
            "bit_rate": bit_rate,
        }

    return profile


def summarize_codec_profiles(profiles: list[CodecProfile]) -> dict[str, Any]:
    return {
        "low": sum(1 for item in profiles if item.risk_level == "LOW"),
        "medium": sum(1 for item in profiles if item.risk_level == "MEDIUM"),
        "high": sum(1 for item in profiles if item.risk_level == "HIGH"),
        "average_score": round(sum(item.realtime_score for item in profiles) / len(profiles), 2) if profiles else 0,
    }


def _category(codec: str) -> str:
    if codec.startswith("hap"):
        return "HAP"
    if codec == "notchlc":
        return "NotchLC"
    if codec.startswith("prores"):
        return "ProRes"
    if codec in {"h264", "avc1"}:
        return "H264"
    if codec in {"hevc", "h265"}:
        return "HEVC"
    return "Other"


def _has_alpha(codec: str, pix_fmt: str) -> bool:
    alpha_formats = {"rgba", "argb", "bgra", "abgr", "yuva420p", "yuva422p", "yuva444p"}
    return pix_fmt in alpha_formats or pix_fmt.startswith("yuva") or "4444" in codec


def _max_risk(left: str, right: str) -> str:
    order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
    return left if order[left] >= order[right] else right


def _fps(value: Any) -> float | None:
    if value in (None, "", "0/0"):
        return None
    try:
        if isinstance(value, str) and "/" in value:
            return float(Fraction(value))
        return float(value)
    except (TypeError, ValueError, ZeroDivisionError):
        return None


def _video_stream(media: Any) -> dict[str, Any]:
    for stream in (getattr(media, "ffprobe", None) or {}).get("streams", []):
        if stream.get("codec_type") == "video":
            return stream
    return {}
