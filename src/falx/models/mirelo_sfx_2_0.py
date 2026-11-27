from __future__ import annotations

from typing import ClassVar, Literal, Self

from pydantic import Field, model_validator

from falx.models import BaseFalConfig


class _MireloSfx20Config(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    num_samples: int = Field(
        default=2,
        ge=1,
        le=4,
        description="Number of variations to generate. Billed per sample.",
    )


class _MireloSfx20AudioConfig(_MireloSfx20Config):
    upload_audio_format: Literal["wav", "mp3", "aac", "flac"] = Field(
        default="wav",
        description="Audio format of each file",
    )
    upload_audio_bitrate_kbps: int | None = Field(
        default=None,
        ge=32,
        le=320,
        description=(
            "Bitrate in kbps for an mp3 or aac upload. mp3 is written at exactly this constant "
            "rate, one of 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320. aac "
            "takes 32 to 256 as a target the encoder may undershoot on mono or sparse audio. "
            "Unset keeps the default: mp3 at LAME V0 VBR, aac at a 256 kbps target. Refused "
            "with a lossless upload_audio_format."
        ),
    )

    @model_validator(mode="after")
    def validate_upload_audio_bitrate(self) -> Self:
        bitrate = self.upload_audio_bitrate_kbps
        if bitrate is None:
            return self
        if self.upload_audio_format in ("wav", "flac"):
            raise ValueError("upload_audio_bitrate_kbps requires mp3 or aac upload_audio_format")
        if self.upload_audio_format == "mp3" and bitrate not in (
            32,
            40,
            48,
            56,
            64,
            80,
            96,
            112,
            128,
            160,
            192,
            224,
            256,
            320,
        ):
            raise ValueError("upload_audio_bitrate_kbps must be a supported mp3 constant bitrate")
        if self.upload_audio_format == "aac" and bitrate > 256:
            raise ValueError("upload_audio_bitrate_kbps must be at most 256 for aac")
        return self


class MireloSfx20TextToAudioConfig(_MireloSfx20AudioConfig):
    app_id: Literal["mirelo-ai/sfx2.0/text-to-audio"]
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="What the sound effect should sound like",
    )
    negative_prompt: str | None = Field(
        default=None,
        max_length=1000,
        description="Sounds to keep out of the result",
    )
    duration: float = Field(
        default=30,
        ge=0.1,
        le=600,
        description="Seconds of sound to generate, up to the deployment's text-to-SFX maximum",
    )
    seed: int | None = Field(
        default=None,
        ge=-1,
        le=9223372036854776000,
        description="Seed of the first sample; -1 or unset is random",
    )


class MireloSfx20VideoToVideoConfig(_MireloSfx20Config):
    app_id: Literal["mirelo-ai/sfx2.0/video-to-video"]
    video_url: str = Field(
        ...,
        description="Video to add sound to: an http(s) URL, or a base64 data URI up to 8 MB.",
    )
    text_prompt: str | None = Field(
        default=None,
        max_length=2000,
        description=(
            "Optional text guiding the soundtrack. Name sounds the picture does not show, "
            "such as off-screen sounds or an ambience bed, to have them worked into it."
        ),
    )
    negative_prompt: str | None = Field(
        default=None,
        max_length=1000,
        description="Sounds to keep out of the result, as a short comma-separated list.",
    )
    preserve_speech: bool = Field(
        default=True,
        description=(
            "Keep the speech in the input's audio and generate the rest of the soundtrack "
            "around it. False generates sound effects only and suppresses speech."
        ),
    )
    duration: float = Field(
        default=10,
        ge=1,
        le=600,
        description=(
            "Seconds of sound to generate, from 1 s to 600 s, clamped to the video's length. "
            "Over 10 s generates in 10 s windows. A video shorter than 1 s answers 400."
        ),
    )
    seed: int | None = Field(
        default=None,
        ge=-1,
        le=18446744073709552000,
        description="Seed for generation. -1 or None for random.",
    )
    num_samples: int = Field(
        default=2,
        ge=1,
        le=4,
        title="Number of Samples",
        description="Number of variations to generate. Billed per sample.",
    )


class MireloSfx20VideoToAudioConfig(MireloSfx20VideoToVideoConfig, _MireloSfx20AudioConfig):
    app_id: Literal["mirelo-ai/sfx2.0/video-to-audio"]
    return_speech: bool = Field(
        default=False,
        description=(
            "Also return the input's separated speech as its own audio file, in the response's "
            "speech. With preserve_speech false the soundtracks are sound effects only and the "
            "speech is separated while they generate. With preserve_speech true it is the "
            "speech separated from the input that the soundtracks were generated around, not "
            "the speech in them: the model renders that speech anew, so the file does not cancel "
            "or double it cleanly when layered onto a soundtrack. The file is mono, in "
            "upload_audio_format, and as long as the soundtracks. It is not billed."
        ),
    )
