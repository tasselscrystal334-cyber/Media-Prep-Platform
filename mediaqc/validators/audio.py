"""Audio stream validator."""

from __future__ import annotations

from . import BaseValidator, get_audio_stream, register_validator


@register_validator
class AudioValidator(BaseValidator):
    name = "audio"
    description = "Validate whether audio streams are allowed."
    severity = "FAIL"

    def validate(self, media):
        audio = get_audio_stream(media)
        if not self.rules.audio.allow_audio and audio:
            return self.result(
                "FAIL",
                "Audio stream found, but project rules do not allow audio.",
                {"codec": audio.get("codec_name")},
            )
        return self.result("PASS", "Audio rule passed.", {"has_audio": bool(audio)})
