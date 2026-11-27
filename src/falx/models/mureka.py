from __future__ import annotations

from typing import Any, ClassVar, Literal, Self

from pydantic import Field, model_validator

from falx.models import BaseFalConfig


class _MurekaBaseConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    enable_safety_checker: bool = Field(
        default=True,
        description="Authorized callers may set false to request relaxed screening.",
    )


class MurekaInstrumentalConfig(_MurekaBaseConfig):
    app_id: Literal["mureka/v8/generate/instrumental", "mureka/v9/generate/instrumental"]
    schema_example_parameters: ClassVar[dict[str, Any]] = {"prompt": "<your prompt here>"}

    prompt: str | None = Field(
        default=None,
        min_length=1,
        max_length=1024,
        description=(
            "Description of the desired instrumental. "
            "Provide exactly one of prompt or instrumental_id."
        ),
    )
    instrumental_id: str | None = Field(
        default=None,
        min_length=1,
        description=(
            "Instrumental ID returned by /files/upload with purpose='instrumental'. "
            "Provide exactly one of instrumental_id or prompt."
        ),
    )

    @model_validator(mode="after")
    def validate_instrumental_source(self) -> Self:
        if (self.prompt is None) == (self.instrumental_id is None):
            raise ValueError("provide exactly one of prompt or instrumental_id")
        return self


class MurekaSongConfig(_MurekaBaseConfig):
    app_id: Literal["mureka/v8/generate/song", "mureka/v9/generate/song"]
    schema_example_parameters: ClassVar[dict[str, Any]] = {"prompt": "<your prompt here>"}

    lyrics: str | None = Field(
        default=None,
        min_length=1,
        max_length=5000,
        description=(
            "Lyrics to sing, up to 5,000 characters. Provide this for lyrics-to-song "
            "generation; otherwise provide prompt for prompt-to-song generation."
        ),
    )
    melody_id: str | None = Field(
        default=None,
        min_length=1,
        description=(
            "Melody ID returned by /files/upload with purpose='melody'. "
            "This cannot be combined with prompt, reference_id, or vocal_id."
        ),
    )
    vocal_id: str | None = Field(
        default=None,
        min_length=1,
        description="Voice ID returned by /voice/clone.",
    )
    styles: (
        list[
            Literal[
                "pop",
                "rock",
                "jazz",
                "r&b",
                "edm",
                "ambient",
                "folk",
                "latin",
                "k-pop",
                "j-pop",
                "house",
                "gospel",
                "lo-fi",
            ]
        ]
        | None
    ) = Field(
        default=None,
        min_length=1,
        description=(
            "One or more music genres for prompt-to-song generation. "
            "This cannot be used when lyrics is provided."
        ),
    )
    reference_id: str | None = Field(
        default=None,
        min_length=1,
        description="Reference-music ID returned by /files/upload with purpose='reference'.",
    )
    prompt: str | None = Field(
        default=None,
        min_length=1,
        max_length=2000,
        description=(
            "Describe the desired song, mood, instrumentation, and vocals. Required when "
            "lyrics is omitted, up to 2,000 characters. With lyrics, it acts as a "
            "music-style control and supports up to 1,024 characters."
        ),
    )
    gender: Literal["female", "male"] | None = Field(
        default=None,
        description=(
            "Preferred vocal gender for lyrics-to-song generation. "
            "An uploaded or cloned voice takes precedence."
        ),
    )

    @model_validator(mode="after")
    def validate_song_inputs(self) -> Self:
        if self.lyrics is None and self.prompt is None:
            raise ValueError("prompt is required when lyrics is omitted")
        if self.lyrics is not None:
            if self.prompt is not None and len(self.prompt) > 1024:
                raise ValueError("prompt supports up to 1024 characters with lyrics")
            if self.styles is not None:
                raise ValueError("styles cannot be used with lyrics")
        if self.melody_id is not None and any(
            value is not None for value in (self.prompt, self.reference_id, self.vocal_id)
        ):
            raise ValueError("melody_id cannot be combined with prompt, reference_id, or vocal_id")
        return self


class MurekaSoundtrackConfig(_MurekaBaseConfig):
    app_id: Literal["mureka/v8/generate/soundtrack", "mureka/v9/generate/soundtrack"]
    schema_example_parameters: ClassVar[dict[str, Any]] = {"image_id": "<uploaded-image-id>"}

    video_id: str | None = Field(
        default=None,
        min_length=1,
        description=(
            "Video ID returned by /files/upload with purpose='soundtrack'. "
            "Provide exactly one of image_id or video_id."
        ),
    )
    audio_start: int | None = Field(
        default=None,
        description=(
            "Start time of the soundtrack audio in milliseconds. If only audio_start is "
            "specified, generation starts there and continues for the video duration, "
            "stopping at the end of the song if the remaining audio is shorter. The "
            "soundtrack audio segment must be at least 3 seconds long, and a 1-second "
            "fade-in is added at the beginning."
        ),
    )
    prompt: str | None = Field(
        default=None,
        min_length=1,
        max_length=1024,
        description="Optional description of the desired soundtrack style and mood.",
    )
    image_id: str | None = Field(
        default=None,
        min_length=1,
        description=(
            "Image ID returned by /files/upload with purpose='soundtrack'. "
            "Provide exactly one of image_id or video_id."
        ),
    )
    audio_end: int | None = Field(
        default=None,
        description=(
            "End time of the soundtrack audio in milliseconds. If both audio_start and "
            "audio_end are specified, generation uses those times. If audio_end exceeds "
            "the song duration, generation stops at the end of the song. The soundtrack "
            "audio segment must be at least 3 seconds long, and a 1-second fade-out is "
            "added at the end."
        ),
    )

    @model_validator(mode="after")
    def validate_soundtrack_inputs(self) -> Self:
        if (self.image_id is None) == (self.video_id is None):
            raise ValueError("provide exactly one of image_id or video_id")
        if (
            self.audio_start is not None
            and self.audio_end is not None
            and self.audio_end - self.audio_start < 3000
        ):
            raise ValueError("audio_end - audio_start must be at least 3000 milliseconds")
        return self


class _MurekaSongSourceConfig(_MurekaBaseConfig):
    schema_example_parameters: ClassVar[dict[str, Any]] = {"song_id": "<generated-song-id>"}

    song_id: str | None = Field(
        default=None,
        min_length=1,
        description=(
            "Generated song ID from song_id in a /generate/song response. "
            "Provide exactly one of song_id or upload_audio_id."
        ),
    )
    upload_audio_id: str | None = Field(
        default=None,
        min_length=1,
        description=(
            "Audio ID returned by /files/upload with purpose='audio'. "
            "Provide exactly one of song_id or upload_audio_id."
        ),
    )

    @model_validator(mode="after")
    def validate_song_source(self) -> Self:
        if (self.song_id is None) == (self.upload_audio_id is None):
            raise ValueError("provide exactly one of song_id or upload_audio_id")
        return self


class MurekaTrackConfig(_MurekaSongSourceConfig):
    app_id: Literal["mureka/v8/generate/track"]

    lyrics: str | None = Field(
        default=None,
        min_length=1,
        max_length=5000,
        description="Lyrics for a generated vocal track, up to 5,000 characters.",
    )
    generate_start: int | None = Field(
        default=None,
        ge=0,
        description="Optional start of the generation region in milliseconds.",
    )
    generate_end: int | None = Field(
        default=None,
        ge=0,
        description=(
            "Optional end of the generation region in milliseconds. "
            "Requires generate_start and must be greater than it."
        ),
    )
    vocal_gender: Literal["female", "male"] | None = Field(
        default=None,
        description="Preferred vocal gender; only valid when generate_type is Vocals.",
    )
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=1024,
        description="Description of the track's music style and performance.",
    )
    generate_type: Literal[
        "Vocals",
        "Instrumental",
        "Drums",
        "Bass",
        "Guitar",
        "Keyboard",
        "Percussion",
        "Strings",
        "Synth",
        "FX",
        "Brass",
        "Woodwinds",
    ] = Field(
        ...,
        description="Type of music or vocal track to generate.",
    )

    @model_validator(mode="after")
    def validate_track_inputs(self) -> Self:
        if self.generate_end is not None and (
            self.generate_start is None or self.generate_end <= self.generate_start
        ):
            raise ValueError("generate_end requires generate_start and must be greater than it")
        if self.vocal_gender is not None and self.generate_type != "Vocals":
            raise ValueError("vocal_gender is only valid when generate_type is Vocals")
        return self


class MurekaSongExtendConfig(_MurekaSongSourceConfig):
    app_id: Literal["mureka/v8/song/extend"]

    lyrics: str = Field(
        ...,
        min_length=1,
        max_length=3000,
        description="Lyrics for the extended section, up to 3,000 characters.",
    )
    extend_type: Literal["tail", "head"] = Field(
        default="tail",
        description="Direction of extension: append to the tail or prepend to the head.",
    )
    extend_at: int = Field(
        ...,
        ge=0,
        description="Timestamp in milliseconds where extension begins.",
    )


class MurekaSongRemixConfig(_MurekaSongSourceConfig):
    app_id: Literal["mureka/v8/song/remix"]

    upload_audio_id: str | None = Field(
        default=None,
        min_length=1,
        description=(
            "Audio ID returned by /files/upload with purpose='remix'. "
            "Provide exactly one of song_id or upload_audio_id."
        ),
    )
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=1024,
        description=(
            "Control the remix's genre, mood, instrumentation, and arrangement with a "
            "prompt, up to 1,024 characters."
        ),
    )
    lyrics: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Complete lyrics for the remixed song, up to 5,000 characters.",
    )


class MurekaFilesUploadConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["mureka/api/files/upload"]
    file_url: str = Field(
        ...,
        description=(
            "Public HTTPS URL or data URI of the file to upload. Files must be 10 MB "
            "(10,485,760 bytes) or smaller, except for purpose='soundtrack', which accepts "
            "videos up to 100 MB (104,857,600 bytes) and images up to 50 MB (52,428,800 bytes)."
        ),
    )
    purpose: Literal[
        "reference",
        "melody",
        "instrumental",
        "voice",
        "audio",
        "remix",
        "soundtrack",
        "lyrics-video",
    ] = Field(
        ...,
        description=(
            "Intended use of the uploaded file. "
            "The returned ID can only be used in parameters that accept this purpose."
        ),
    )
