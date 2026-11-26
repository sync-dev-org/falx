from __future__ import annotations

import warnings
from types import NoneType, UnionType
from typing import Annotated, Any, ClassVar, Literal, Union, cast, get_args, get_origin

from pydantic import (
    BaseModel,
    ConfigDict,
    Discriminator,
    Field,
    TypeAdapter,
    field_validator,
    model_validator,
)


class BaseFalConfig(BaseModel):
    """Base class for registered fal model configurations."""

    model_config = ConfigDict(extra="forbid")
    random_seed_field: ClassVar[str | None] = None


class MatrixAxis(BaseModel):
    """One axis of the matrix sweep.

    An axis can vary one parameter field with ``field``/``values`` or vary
    multiple parameter fields as synchronized units with ``fields``/``value_set``.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    field: str | None = Field(
        default=None,
        description="Parameter field name to vary across this axis.",
    )
    values: list[Any] | None = Field(
        default=None,
        min_length=1,
        description="Values to substitute into parameters[field] for each cell.",
    )
    fields: list[str] | None = Field(
        default=None,
        min_length=1,
        description="Parameter field names to vary together across this axis.",
    )
    value_set: list[list[Any]] | None = Field(
        default=None,
        min_length=1,
        description=(
            "Rows of synchronized values to substitute into parameters[fields[N]]. "
            "Each row length must match fields; null values leave that field unchanged."
        ),
    )

    @model_validator(mode="after")
    def validate_axis_shape(self) -> MatrixAxis:
        if self.field is not None and self.fields is not None:
            raise ValueError("matrix axis field and fields are mutually exclusive")
        if self.values is not None and self.value_set is not None:
            raise ValueError("matrix axis values and value_set are mutually exclusive")

        uses_single_axis = self.field is not None or self.values is not None
        uses_multi_axis = self.fields is not None or self.value_set is not None
        if uses_single_axis and uses_multi_axis:
            raise ValueError(
                "matrix axis field/values and fields/value_set are mutually exclusive"
            )

        if uses_single_axis:
            if self.field is None or self.values is None:
                raise ValueError("matrix axis must use field/values together")
            return self

        if uses_multi_axis:
            if self.fields is None or self.value_set is None:
                raise ValueError("matrix axis must use fields/value_set together")
            field_count = len(self.fields)
            for index, values in enumerate(self.value_set, start=1):
                if len(values) != field_count:
                    raise ValueError(
                        "matrix axis value_set item "
                        f"{index} has {len(values)} value(s), expected {field_count}"
                    )
            return self

        raise ValueError("matrix axis must use field/values or fields/value_set")

    @property
    def parameter_fields(self) -> tuple[str, ...]:
        if self.fields is not None:
            return tuple(self.fields)
        if self.field is not None:
            return (self.field,)
        return ()

    @property
    def replacement_groups(self) -> tuple[tuple[Any, ...], ...]:
        if self.value_set is not None:
            return tuple(tuple(values) for values in self.value_set)
        if self.values is not None:
            return tuple((value,) for value in self.values)
        return ()


class MatrixAxes(BaseModel):
    """Matrix sweep configuration: expansion mode + axis list.

    Stage 1 supports cartesian mode only; zip mode is reserved for a follow-up issue.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    mode: Literal["cartesian"] = Field(
        ...,
        description="Expansion mode. Only 'cartesian' is implemented in stage 1.",
    )
    axes: list[MatrixAxis] = Field(
        ...,
        min_length=1,
        description="At least one axis is required.",
    )


class JobConfig(BaseModel):
    """Validated pure-input YAML schema for falx job config files."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    app_id: str
    parameters: dict[str, Any]
    output_dir: str | None = None
    iterations: int = Field(default=1, ge=1)
    slug: str
    version: int = Field(ge=1)
    max_concurrency: int = Field(
        default=8,
        ge=1,
        description=(
            "Upper bound on fal.ai concurrent in-flight submits. Shared between matrix "
            "cells and non-matrix iteration loops. Overridable via --max-concurrency."
        ),
    )
    output_expiration_seconds: int | None = Field(default=None, ge=1)
    matrix_axes: MatrixAxes | None = Field(
        default=None,
        description=(
            "Optional matrix sweep section. When set, falx expands the job into "
            "one cell per axis combination; when omitted, behaves as a single submit."
        ),
    )

    @field_validator("output_dir", mode="before")
    @classmethod
    def normalize_output_dir(cls, value: Any) -> Any:
        if not isinstance(value, str) and hasattr(value, "__fspath__"):
            return value.__fspath__()
        return value

    @model_validator(mode="before")
    @classmethod
    def reject_legacy_v041_shape(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value

        legacy_fields = {
            "results",
            "request_id",
            "submitted_at",
            "completed_at",
            "result",
            "error_type",
            "error",
        }
        if legacy_fields.intersection(value):
            raise ValueError(
                "job YAML is input-only; request state and results belong in caller metadata."
            )
        return value

    @model_validator(mode="after")
    def validate_matrix_axes_fields_exist_in_parameters(self) -> JobConfig:
        if self.matrix_axes is None:
            return self
        missing = [
            field
            for axis in self.matrix_axes.axes
            for field in axis.parameter_fields
            if field not in self.parameters
        ]
        if missing:
            raise ValueError(f"matrix_axes.axes references unknown parameter field(s): {missing!r}")
        return self


from falx.models.bria_increase_resolution import BriaIncreaseResolutionConfig  # noqa: E402
from falx.models.bria_video_background_removal_green_screen_despill import (  # noqa: E402
    BriaVideoBackgroundRemovalGreenScreenDespillConfig,
    BriaVideoOutputContainerAndCodec,
)
from falx.models.flux_3_common import Flux3Keyframe  # noqa: E402
from falx.models.flux_3_edit_video import Flux3EditVideoConfig  # noqa: E402
from falx.models.flux_3_extend_video import Flux3ExtendVideoConfig  # noqa: E402
from falx.models.flux_3_first_last_frame_to_video import (  # noqa: E402
    Flux3FirstLastFrameToVideoConfig,
)
from falx.models.flux_3_image_to_video import Flux3ImageToVideoConfig  # noqa: E402
from falx.models.flux_3_keyframes_to_video import (  # noqa: E402
    Flux3KeyframesToVideoConfig,
)
from falx.models.flux_3_text_to_video import Flux3TextToVideoConfig  # noqa: E402
from falx.models.flux_video_upscale import FluxVideoUpscaleConfig  # noqa: E402
from falx.models.gemini_3_1_flash_tts import Gemini31FlashTtsConfig  # noqa: E402
from falx.models.gemini_3_8_flash_lite_tts import Gemini38FlashLiteTtsConfig  # noqa: E402
from falx.models.gemini_3_8_flash_tts import Gemini38FlashTtsConfig  # noqa: E402
from falx.models.gemini_omni_flash_edit import (  # noqa: E402
    GeminiOmniFlashEditConfig,
)
from falx.models.gemini_omni_flash_image_to_video import (  # noqa: E402
    GeminiOmniFlashImageToVideoConfig,
)
from falx.models.gemini_omni_flash_reference_to_video import (  # noqa: E402
    GeminiOmniFlashReferenceToVideoConfig,
)
from falx.models.gemini_omni_flash_text_to_video import (  # noqa: E402
    GeminiOmniFlashTextToVideoConfig,
)
from falx.models.gemini_omni_flash_v1_1_edit import (  # noqa: E402
    GeminiOmniFlashV11EditConfig,
)
from falx.models.gemini_omni_flash_v1_1_image_to_video import (  # noqa: E402
    GeminiOmniFlashV11ImageToVideoConfig,
)
from falx.models.gemini_omni_flash_v1_1_reference_to_video import (  # noqa: E402
    GeminiOmniFlashV11ReferenceToVideoConfig,
)
from falx.models.gemini_omni_flash_v1_1_text_to_video import (  # noqa: E402
    GeminiOmniFlashV11TextToVideoConfig,
)
from falx.models.gemini_omni_flash_v1_2_edit import (  # noqa: E402
    GeminiOmniFlashV12EditConfig,
)
from falx.models.gemini_omni_flash_v1_2_extend import (  # noqa: E402
    GeminiOmniFlashV12ExtendConfig,
)
from falx.models.gemini_omni_flash_v1_2_image_to_video import (  # noqa: E402
    GeminiOmniFlashV12ImageToVideoConfig,
)
from falx.models.gemini_omni_flash_v1_2_reference_to_video import (  # noqa: E402
    GeminiOmniFlashV12ReferenceToVideoConfig,
)
from falx.models.gemini_omni_flash_v1_2_text_to_video import (  # noqa: E402
    GeminiOmniFlashV12TextToVideoConfig,
)
from falx.models.gemini_omni_flash_v1_2_upscale import (  # noqa: E402
    GeminiOmniFlashV12UpscaleConfig,
)
from falx.models.gemini_tts import GeminiTtsConfig  # noqa: E402
from falx.models.gemini_tts_common import (  # noqa: E402
    Gemini38SpeechTurn,
    Gemini38TtsSpeaker,
    GeminiTtsLanguage,
    GeminiTtsSpeaker,
    GeminiTtsVoice,
)
from falx.models.gpt_image_2 import GptImage2Config, ImageSize  # noqa: E402
from falx.models.gpt_image_2_5 import (  # noqa: E402
    GptImage25FlareTextToImageConfig,
    GptImage25SunburstTextToImageConfig,
)
from falx.models.gpt_image_2_5_edit import (  # noqa: E402
    GptImage25FlareEditConfig,
    GptImage25SunburstEditConfig,
)
from falx.models.gpt_image_2_edit import GptImage2EditConfig  # noqa: E402
from falx.models.grok_imagine_image_v2_0 import (  # noqa: E402
    GrokImagineImageV20AspectRatio,
    GrokImagineImageV20BaseConfig,
    GrokImagineImageV20TextToImageConfig,
)
from falx.models.grok_imagine_image_v2_0_edit import (  # noqa: E402
    GrokImagineImageV20EditAspectRatio,
    GrokImagineImageV20EditConfig,
)
from falx.models.grok_imagine_video_v1_5_image_to_video import (  # noqa: E402
    GrokImagineVideoV15ImageToVideoConfig,
)
from falx.models.grok_imagine_video_v1_5_reference_to_video import (  # noqa: E402
    GrokImagineVideoV15ReferenceResolution,
    GrokImagineVideoV15ReferenceToVideoConfig,
)
from falx.models.grok_imagine_video_v1_5_text_to_video import (  # noqa: E402
    GrokImagineVideoV15AspectRatio,
    GrokImagineVideoV15Resolution,
    GrokImagineVideoV15TextToVideoConfig,
)
from falx.models.happy_horse_image_to_video import HappyHorseImageToVideoConfig  # noqa: E402
from falx.models.happy_horse_reference_to_video import (  # noqa: E402
    HappyHorseReferenceToVideoConfig,
)
from falx.models.happy_horse_text_to_video import HappyHorseTextToVideoConfig  # noqa: E402
from falx.models.happy_horse_video_edit import HappyHorseVideoEditConfig  # noqa: E402
from falx.models.ideogram_v4 import (  # noqa: E402
    IdeogramV4Config,
    IdeogramV4ImageSize,
)
from falx.models.kling_o3_4k_image_to_video import (  # noqa: E402
    KlingVideoO34kImageToVideoConfig,
)
from falx.models.kling_o3_4k_reference_to_video import (  # noqa: E402
    KlingVideoO34kReferenceToVideoConfig,
)
from falx.models.kling_o3_4k_text_to_video import (  # noqa: E402
    KlingVideoO34kTextToVideoConfig,
)
from falx.models.kling_o3_4k_video_to_video_edit import (  # noqa: E402
    KlingVideoO34kVideoToVideoEditConfig,
)
from falx.models.kling_o3_4k_video_to_video_reference import (  # noqa: E402
    KlingO34kVideoToVideoAspectRatio,
    KlingVideoO34kVideoToVideoReferenceConfig,
)
from falx.models.kling_o3_common import (  # noqa: E402
    KlingO3ComboElementInput,
    KlingO3ImageElementInput,
    KlingO3MultiPromptElement,
)
from falx.models.kling_o3_pro_image_to_video import (  # noqa: E402
    KlingVideoO3ProImageToVideoConfig,
)
from falx.models.kling_o3_pro_reference_to_video import (  # noqa: E402
    KlingVideoO3ProReferenceToVideoConfig,
)
from falx.models.kling_o3_pro_text_to_video import (  # noqa: E402
    KlingVideoO3ProTextToVideoConfig,
)
from falx.models.kling_o3_pro_video_to_video_edit import (  # noqa: E402
    KlingVideoO3ProVideoToVideoEditConfig,
)
from falx.models.kling_v3_4k_image_to_video import (  # noqa: E402
    KlingVideoV34kImageToVideoConfig,
)
from falx.models.kling_v3_4k_text_to_video import (  # noqa: E402
    KlingVideoV34kTextToVideoConfig,
)
from falx.models.kling_v3_common import (  # noqa: E402
    KlingV3ComboElementInput,
    KlingV3MultiPromptElement,
)
from falx.models.kling_v3_motion_control import (  # noqa: E402
    KlingV3ImageElementInput,
    KlingVideoV3ProMotionControlConfig,
)
from falx.models.kling_v3_pro_image_to_video import (  # noqa: E402
    KlingVideoV3ProImageToVideoConfig,
)
from falx.models.kling_v3_pro_text_to_video import (  # noqa: E402
    KlingVideoV3ProTextToVideoConfig,
)
from falx.models.luma_ray_3_2_common import (  # noqa: E402
    LumaRay32EditControls,
    LumaRay32EditDepthControl,
    LumaRay32EditFaceControl,
    LumaRay32EditNormalsControl,
    LumaRay32EditPoseControl,
    LumaRay32EditTrajectoryControl,
    LumaRay32ReframeSourcePosition,
)
from falx.models.luma_ray_3_2_image_to_video import (  # noqa: E402
    LumaRay32ImageToVideoConfig,
)
from falx.models.luma_ray_3_2_reframe import LumaRay32ReframeConfig  # noqa: E402
from falx.models.luma_ray_3_2_text_to_video import (  # noqa: E402
    LumaRay32TextToVideoConfig,
)
from falx.models.luma_ray_3_2_video_to_video import (  # noqa: E402
    LumaRay32VideoToVideoConfig,
)
from falx.models.lyria2 import Lyria2Config  # noqa: E402
from falx.models.lyria3 import Lyria3Config  # noqa: E402
from falx.models.lyria3_pro import Lyria3ProConfig  # noqa: E402
from falx.models.lyria_3_5 import Lyria35Config  # noqa: E402
from falx.models.meshy_v7_text_to_3d import MeshyV7TextTo3dConfig  # noqa: E402
from falx.models.minimax_h3_max_camera_controls import (  # noqa: E402
    H3MaxCameraKeyframe,
    MinimaxH3MaxCameraControlsConfig,
)
from falx.models.minimax_h3_max_image_to_video import (  # noqa: E402
    MinimaxH3MaxImageToVideoConfig,
)
from falx.models.minimax_h3_max_reference_to_video import (  # noqa: E402
    MinimaxH3MaxReferenceToVideoConfig,
)
from falx.models.minimax_h3_max_text_to_video import (  # noqa: E402
    MinimaxH3MaxTextToVideoConfig,
)
from falx.models.minimax_h3_max_turbo_image_to_video import (  # noqa: E402
    MinimaxH3MaxTurboImageToVideoConfig,
)
from falx.models.minimax_h3_max_turbo_text_to_video import (  # noqa: E402
    MinimaxH3MaxTurboTextToVideoConfig,
)
from falx.models.minimax_music_3 import MinimaxMusic3Config  # noqa: E402
from falx.models.muse_image import (  # noqa: E402
    MuseImageAspectRatio,
    MuseImageBaseConfig,
    MuseImageTextToImageConfig,
)
from falx.models.muse_image_edit import MuseImageEditConfig  # noqa: E402
from falx.models.nano_banana import NanoBananaConfig  # noqa: E402
from falx.models.nano_banana_2 import NanoBanana2Config  # noqa: E402
from falx.models.nano_banana_2_1 import NanoBanana21Config  # noqa: E402
from falx.models.nano_banana_2_1_edit import NanoBanana21EditConfig  # noqa: E402
from falx.models.nano_banana_2_edit import NanoBanana2EditConfig  # noqa: E402
from falx.models.nano_banana_edit import NanoBananaEditConfig  # noqa: E402
from falx.models.nano_banana_lite import NanoBananaLiteConfig  # noqa: E402
from falx.models.nano_banana_lite_edit import NanoBananaLiteEditConfig  # noqa: E402
from falx.models.nano_banana_pro import NanoBananaProConfig  # noqa: E402
from falx.models.nano_banana_pro_edit import NanoBananaProEditConfig  # noqa: E402
from falx.models.qwen_audio_3_tts import QwenAudio3TtsConfig  # noqa: E402
from falx.models.qwen_image_3_common import QwenImage3ImageSize  # noqa: E402
from falx.models.qwen_image_3_edit import QwenImage3EditConfig  # noqa: E402
from falx.models.qwen_image_3_text_to_image import (  # noqa: E402
    QwenImage3TextToImageConfig,
)
from falx.models.sam_3_1_common import (  # noqa: E402
    Sam31BoxPrompt,
    Sam31BoxPromptBase,
    Sam31ImageOutputFormat,
    Sam31Label,
    Sam31PointPrompt,
    Sam31PointPromptBase,
    Sam31VideoOutputType,
)
from falx.models.sam_3_1_image import Sam31ImageConfig  # noqa: E402
from falx.models.sam_3_1_image_rle import Sam31ImageRleConfig  # noqa: E402
from falx.models.sam_3_1_video import Sam31VideoConfig  # noqa: E402
from falx.models.sam_3_1_video_rle import Sam31VideoRleConfig  # noqa: E402
from falx.models.seedance2_fast_image_to_video import (  # noqa: E402
    Seedance2FastImageToVideoConfig,
)
from falx.models.seedance2_fast_reference_to_video import (  # noqa: E402
    Seedance2FastReferenceToVideoConfig,
)
from falx.models.seedance2_fast_text_to_video import (  # noqa: E402
    Seedance2FastTextToVideoConfig,
)
from falx.models.seedance2_image_to_video import Seedance2ImageToVideoConfig  # noqa: E402
from falx.models.seedance2_mini_image_to_video import (  # noqa: E402
    Seedance2MiniImageToVideoConfig,
)
from falx.models.seedance2_mini_reference_to_video import (  # noqa: E402
    Seedance2MiniReferenceToVideoConfig,
)
from falx.models.seedance2_mini_text_to_video import (  # noqa: E402
    Seedance2MiniTextToVideoConfig,
)
from falx.models.seedance2_reference_to_video import Seedance2ReferenceToVideoConfig  # noqa: E402
from falx.models.seedance2_text_to_video import Seedance2TextToVideoConfig  # noqa: E402
from falx.models.seedance25_image_to_video import Seedance25ImageToVideoConfig  # noqa: E402
from falx.models.seedance25_reference_to_video import (  # noqa: E402
    Seedance25ReferenceToVideoConfig,
)
from falx.models.seedance25_text_to_video import Seedance25TextToVideoConfig  # noqa: E402
from falx.models.seedream_v5_lite_edit import SeedreamV5LiteEditConfig  # noqa: E402
from falx.models.seedream_v5_lite_text_to_image import (  # noqa: E402
    SeedreamV5LiteImageSize,
    SeedreamV5LiteTextToImageConfig,
)
from falx.models.seedream_v5_pro_common import SeedreamV5ProImageSize  # noqa: E402
from falx.models.seedream_v5_pro_edit import SeedreamV5ProEditConfig  # noqa: E402
from falx.models.seedream_v5_pro_layerize import SeedreamV5ProLayerizeConfig  # noqa: E402
from falx.models.seedream_v5_pro_text_to_image import (  # noqa: E402
    SeedreamV5ProTextToImageConfig,
)
from falx.models.seedream_v45_edit import SeedreamV45EditConfig  # noqa: E402
from falx.models.seedream_v45_text_to_image import (  # noqa: E402
    SeedreamV45ImageSize,
    SeedreamV45TextToImageConfig,
)
from falx.models.sonilo_v1_1_video_to_sound_effects import (  # noqa: E402
    SoniloV11SfxSegment,
    SoniloV11VideoToSoundEffectsConfig,
)
from falx.models.topaz_deblur_video import TopazDeblurVideoConfig  # noqa: E402
from falx.models.topaz_interpolate_video import TopazInterpolateVideoConfig  # noqa: E402
from falx.models.topaz_upscale_image_creative import (  # noqa: E402
    TopazUpscaleImageCreativeConfig,
)
from falx.models.topaz_upscale_image_generative import (  # noqa: E402
    TopazUpscaleImageGenerativeConfig,
)
from falx.models.topaz_upscale_image_precision import (  # noqa: E402
    TopazUpscaleImagePrecisionConfig,
)
from falx.models.topaz_upscale_image_transparent import (  # noqa: E402
    TopazUpscaleImageTransparentConfig,
)
from falx.models.veo3_1_extend_video import Veo31ExtendVideoConfig  # noqa: E402
from falx.models.veo3_1_first_last_frame_to_video import (  # noqa: E402
    Veo31FirstLastFrameToVideoConfig,
)
from falx.models.veo3_1_image_to_video import Veo31ImageToVideoConfig  # noqa: E402
from falx.models.veo3_1_lite_first_last_frame_to_video import (  # noqa: E402
    Veo31LiteFirstLastFrameToVideoConfig,
)
from falx.models.veo3_1_lite_image_to_video import Veo31LiteImageToVideoConfig  # noqa: E402
from falx.models.veo3_1_lite_text_to_video import Veo31LiteTextToVideoConfig  # noqa: E402
from falx.models.veo3_1_reference_to_video import (  # noqa: E402
    Veo31ReferenceToVideoConfig,
)
from falx.models.veo3_1_text_to_video import Veo31TextToVideoConfig  # noqa: E402
from falx.models.veo3_image_to_video import Veo3ImageToVideoConfig  # noqa: E402
from falx.models.veo3_text_to_video import Veo3TextToVideoConfig  # noqa: E402
from falx.models.vggt_1b import Vggt1bConfig  # noqa: E402
from falx.models.vidu_q3_image_to_video import ViduQ3ImageToVideoConfig  # noqa: E402
from falx.models.vidu_q3_reference_to_video import (  # noqa: E402
    ViduQ3ReferenceToVideoConfig,
)
from falx.models.vidu_q3_reference_to_video_mix import (  # noqa: E402
    ViduQ3ReferenceToVideoMixConfig,
)
from falx.models.vidu_q3_text_to_video import ViduQ3TextToVideoConfig  # noqa: E402
from falx.models.virtual_try_on import VirtualTryOnConfig  # noqa: E402
from falx.models.wan_3_0_prime_image_to_video import (  # noqa: E402
    Wan30PrimeImageToVideoConfig,
)
from falx.models.wan_3_0_prime_reference_to_video import (  # noqa: E402
    Wan30PrimeReferenceToVideoConfig,
)
from falx.models.wan_3_0_prime_text_to_video import (  # noqa: E402
    Wan30PrimeTextToVideoConfig,
)

FalConfig = Annotated[
    BriaIncreaseResolutionConfig
    | BriaVideoBackgroundRemovalGreenScreenDespillConfig
    | Flux3EditVideoConfig
    | Flux3ExtendVideoConfig
    | Flux3FirstLastFrameToVideoConfig
    | Flux3ImageToVideoConfig
    | Flux3KeyframesToVideoConfig
    | Flux3TextToVideoConfig
    | FluxVideoUpscaleConfig
    | Gemini31FlashTtsConfig
    | Gemini38FlashLiteTtsConfig
    | Gemini38FlashTtsConfig
    | GptImage2Config
    | GptImage2EditConfig
    | GptImage25FlareTextToImageConfig
    | GptImage25SunburstTextToImageConfig
    | GptImage25FlareEditConfig
    | GptImage25SunburstEditConfig
    | GeminiOmniFlashEditConfig
    | GeminiOmniFlashImageToVideoConfig
    | GeminiOmniFlashReferenceToVideoConfig
    | GeminiOmniFlashTextToVideoConfig
    | GeminiOmniFlashV11EditConfig
    | GeminiOmniFlashV11ImageToVideoConfig
    | GeminiOmniFlashV11ReferenceToVideoConfig
    | GeminiOmniFlashV11TextToVideoConfig
    | GeminiOmniFlashV12EditConfig
    | GeminiOmniFlashV12ExtendConfig
    | GeminiOmniFlashV12ImageToVideoConfig
    | GeminiOmniFlashV12ReferenceToVideoConfig
    | GeminiOmniFlashV12TextToVideoConfig
    | GeminiOmniFlashV12UpscaleConfig
    | GeminiTtsConfig
    | GrokImagineImageV20EditConfig
    | GrokImagineImageV20TextToImageConfig
    | GrokImagineVideoV15ImageToVideoConfig
    | GrokImagineVideoV15ReferenceToVideoConfig
    | GrokImagineVideoV15TextToVideoConfig
    | HappyHorseImageToVideoConfig
    | HappyHorseReferenceToVideoConfig
    | HappyHorseTextToVideoConfig
    | HappyHorseVideoEditConfig
    | IdeogramV4Config
    | KlingVideoO34kImageToVideoConfig
    | KlingVideoO34kReferenceToVideoConfig
    | KlingVideoO34kTextToVideoConfig
    | KlingVideoO34kVideoToVideoEditConfig
    | KlingVideoO34kVideoToVideoReferenceConfig
    | KlingVideoO3ProImageToVideoConfig
    | KlingVideoO3ProReferenceToVideoConfig
    | KlingVideoO3ProTextToVideoConfig
    | KlingVideoO3ProVideoToVideoEditConfig
    | KlingVideoV34kImageToVideoConfig
    | KlingVideoV34kTextToVideoConfig
    | KlingVideoV3ProImageToVideoConfig
    | KlingVideoV3ProMotionControlConfig
    | KlingVideoV3ProTextToVideoConfig
    | LumaRay32ImageToVideoConfig
    | LumaRay32ReframeConfig
    | LumaRay32TextToVideoConfig
    | LumaRay32VideoToVideoConfig
    | Lyria2Config
    | Lyria3Config
    | Lyria3ProConfig
    | Lyria35Config
    | MeshyV7TextTo3dConfig
    | MinimaxH3MaxCameraControlsConfig
    | MinimaxH3MaxImageToVideoConfig
    | MinimaxH3MaxReferenceToVideoConfig
    | MinimaxH3MaxTextToVideoConfig
    | MinimaxH3MaxTurboImageToVideoConfig
    | MinimaxH3MaxTurboTextToVideoConfig
    | MinimaxMusic3Config
    | MuseImageEditConfig
    | MuseImageTextToImageConfig
    | NanoBanana2Config
    | NanoBanana2EditConfig
    | NanoBanana21Config
    | NanoBanana21EditConfig
    | NanoBananaConfig
    | NanoBananaEditConfig
    | NanoBananaLiteConfig
    | NanoBananaLiteEditConfig
    | NanoBananaProConfig
    | NanoBananaProEditConfig
    | QwenAudio3TtsConfig
    | QwenImage3EditConfig
    | QwenImage3TextToImageConfig
    | Sam31ImageConfig
    | Sam31ImageRleConfig
    | Sam31VideoConfig
    | Sam31VideoRleConfig
    | SeedreamV45EditConfig
    | SeedreamV45TextToImageConfig
    | SeedreamV5LiteEditConfig
    | SeedreamV5LiteTextToImageConfig
    | SeedreamV5ProEditConfig
    | SeedreamV5ProLayerizeConfig
    | SeedreamV5ProTextToImageConfig
    | Seedance2FastImageToVideoConfig
    | Seedance2FastReferenceToVideoConfig
    | Seedance2FastTextToVideoConfig
    | Seedance2ImageToVideoConfig
    | Seedance2MiniImageToVideoConfig
    | Seedance2MiniReferenceToVideoConfig
    | Seedance2MiniTextToVideoConfig
    | Seedance2ReferenceToVideoConfig
    | Seedance2TextToVideoConfig
    | Seedance25ImageToVideoConfig
    | Seedance25ReferenceToVideoConfig
    | Seedance25TextToVideoConfig
    | SoniloV11VideoToSoundEffectsConfig
    | TopazDeblurVideoConfig
    | TopazInterpolateVideoConfig
    | TopazUpscaleImageCreativeConfig
    | TopazUpscaleImageGenerativeConfig
    | TopazUpscaleImagePrecisionConfig
    | TopazUpscaleImageTransparentConfig
    | Veo31ExtendVideoConfig
    | Veo31FirstLastFrameToVideoConfig
    | Veo31ImageToVideoConfig
    | Veo31LiteFirstLastFrameToVideoConfig
    | Veo31LiteImageToVideoConfig
    | Veo31LiteTextToVideoConfig
    | Veo31ReferenceToVideoConfig
    | Veo31TextToVideoConfig
    | Veo3ImageToVideoConfig
    | Veo3TextToVideoConfig
    | Vggt1bConfig
    | ViduQ3ImageToVideoConfig
    | ViduQ3ReferenceToVideoConfig
    | ViduQ3ReferenceToVideoMixConfig
    | ViduQ3TextToVideoConfig
    | VirtualTryOnConfig
    | Wan30PrimeImageToVideoConfig
    | Wan30PrimeReferenceToVideoConfig
    | Wan30PrimeTextToVideoConfig,
    Discriminator("app_id"),
]

SUPPORTED_APP_IDS = frozenset(
    {
        "fal-ai/gemini-tts",
        "fal-ai/gemini-3.1-flash-tts",
        "google/gemini-3.8-flash-tts",
        "google/gemini-3.8-flash-lite-tts",
        "fal-ai/lyria2",
        "fal-ai/lyria3",
        "fal-ai/lyria3/pro",
        "google/lyria-3.5",
        "google/virtual-try-on",
        "alibaba/happy-horse/image-to-video",
        "alibaba/happy-horse/reference-to-video",
        "alibaba/happy-horse/text-to-video",
        "alibaba/happy-horse/video-edit",
        "alibaba/qwen-audio-3-tts",
        "alibaba/qwen-image-3/edit",
        "alibaba/qwen-image-3/text-to-image",
        "alibaba/wan-3.0-prime/image-to-video",
        "alibaba/wan-3.0-prime/reference-to-video",
        "alibaba/wan-3.0-prime/text-to-video",
        "blackforestlabs/flux-3/extend-video",
        "blackforestlabs/flux-3/edit-video",
        "blackforestlabs/flux-3/first-last-frame-to-video",
        "blackforestlabs/flux-3/image-to-video",
        "blackforestlabs/flux-3/keyframes-to-video",
        "blackforestlabs/flux-3/text-to-video",
        "blackforestlabs/flux-video-upscale",
        "bria/increase-resolution",
        "bria/video/background-removal/green-screen-despill",
        "bytedance/seedance-2.0/fast/image-to-video",
        "bytedance/seedance-2.0/fast/reference-to-video",
        "bytedance/seedance-2.0/fast/text-to-video",
        "bytedance/seedance-2.0/image-to-video",
        "bytedance/seedance-2.0/mini/image-to-video",
        "bytedance/seedance-2.0/mini/reference-to-video",
        "bytedance/seedance-2.0/mini/text-to-video",
        "bytedance/seedance-2.0/reference-to-video",
        "bytedance/seedance-2.0/text-to-video",
        "bytedance/seedance-2.5/image-to-video",
        "bytedance/seedance-2.5/reference-to-video",
        "bytedance/seedance-2.5/text-to-video",
        "bytedance/seedream/v5/pro/edit",
        "bytedance/seedream/v5/pro/layerize",
        "bytedance/seedream/v5/pro/text-to-image",
        "fal-ai/kling-video/o3/4k/image-to-video",
        "fal-ai/kling-video/o3/4k/reference-to-video",
        "fal-ai/kling-video/o3/4k/text-to-video",
        "fal-ai/kling-video/o3/4k/video-to-video/edit",
        "fal-ai/kling-video/o3/4k/video-to-video/reference",
        "fal-ai/kling-video/o3/pro/image-to-video",
        "fal-ai/kling-video/o3/pro/reference-to-video",
        "fal-ai/kling-video/o3/pro/text-to-video",
        "fal-ai/kling-video/o3/pro/video-to-video/edit",
        "fal-ai/kling-video/v3/4k/image-to-video",
        "fal-ai/kling-video/v3/4k/text-to-video",
        "fal-ai/kling-video/v3/pro/image-to-video",
        "fal-ai/kling-video/v3/pro/motion-control",
        "fal-ai/kling-video/v3/pro/text-to-video",
        "fal-ai/bytedance/seedream/v4.5/edit",
        "fal-ai/bytedance/seedream/v4.5/text-to-image",
        "fal-ai/bytedance/seedream/v5/lite/edit",
        "fal-ai/bytedance/seedream/v5/lite/text-to-image",
        "fal-ai/nano-banana-2",
        "fal-ai/nano-banana-2/edit",
        "google/nano-banana-2.1",
        "google/nano-banana-2.1/edit",
        "fal-ai/nano-banana",
        "fal-ai/nano-banana/edit",
        "fal-ai/gemini-25-flash-image",
        "fal-ai/gemini-25-flash-image/edit",
        "fal-ai/nano-banana-pro",
        "fal-ai/nano-banana-pro/edit",
        "fal-ai/gemini-3-pro-image-preview",
        "fal-ai/gemini-3-pro-image-preview/edit",
        "fal-ai/gemini-3.1-flash-image-preview",
        "fal-ai/gemini-3.1-flash-image-preview/edit",
        "google/nano-banana-lite",
        "google/nano-banana-lite/edit",
        "fal-ai/sam-3-1/image",
        "fal-ai/sam-3-1/image-rle",
        "fal-ai/sam-3-1/video",
        "fal-ai/sam-3-1/video-rle",
        "google/gemini-omni-flash",
        "google/gemini-omni-flash/edit",
        "google/gemini-omni-flash/image-to-video",
        "google/gemini-omni-flash/reference-to-video",
        "google/gemini-omni-flash/v1.1/edit",
        "google/gemini-omni-flash/v1.1/image-to-video",
        "google/gemini-omni-flash/v1.1/reference-to-video",
        "google/gemini-omni-flash/v1.1/text-to-video",
        "google/gemini-omni-flash/v1.2/edit",
        "google/gemini-omni-flash/v1.2/extend",
        "google/gemini-omni-flash/v1.2/image-to-video",
        "google/gemini-omni-flash/v1.2/reference-to-video",
        "google/gemini-omni-flash/v1.2/text-to-video",
        "google/gemini-omni-flash/v1.2/upscale",
        "ideogram/v4",
        "openai/gpt-image-2",
        "openai/gpt-image-2/edit",
        "openai/gpt-image-2.5/flare/edit",
        "openai/gpt-image-2.5/flare/text-to-image",
        "openai/gpt-image-2.5/sunburst/edit",
        "openai/gpt-image-2.5/sunburst/text-to-image",
        "topaz/deblur/video",
        "topaz/interpolate/video",
        "fal-ai/veo3",
        "fal-ai/veo3/fast",
        "fal-ai/veo3/image-to-video",
        "fal-ai/veo3/fast/image-to-video",
        "fal-ai/veo3.1",
        "fal-ai/veo3.1/extend-video",
        "fal-ai/veo3.1/fast",
        "fal-ai/veo3.1/fast/extend-video",
        "fal-ai/veo3.1/fast/first-last-frame-to-video",
        "fal-ai/veo3.1/fast/image-to-video",
        "fal-ai/veo3.1/fast/reference-to-video",
        "fal-ai/veo3.1/first-last-frame-to-video",
        "fal-ai/veo3.1/image-to-video",
        "fal-ai/veo3.1/lite",
        "fal-ai/veo3.1/lite/first-last-frame-to-video",
        "fal-ai/veo3.1/lite/image-to-video",
        "fal-ai/veo3.1/reference-to-video",
        "fal-ai/vggt-1b",
        "fal-ai/vidu/q3/image-to-video",
        "fal-ai/vidu/q3/reference-to-video",
        "fal-ai/vidu/q3/reference-to-video/mix",
        "fal-ai/vidu/q3/text-to-video",
        "luma/agent/ray/v3.2/image-to-video",
        "luma/agent/ray/v3.2/reframe",
        "luma/agent/ray/v3.2/text-to-video",
        "luma/agent/ray/v3.2/video-to-video",
        "meshy/v7/text-to-3d",
        "minimax/h3-max/camera-controls",
        "minimax/h3-max/image-to-video",
        "minimax/h3-max/reference-to-video",
        "minimax/h3-max/text-to-video",
        "minimax/h3-max-turbo/image-to-video",
        "minimax/h3-max-turbo/text-to-video",
        "minimax/music-3",
        "meta/muse-image/edit",
        "meta/muse-image/text-to-image",
        "sonilo/v1.1/video-to-sound-effects",
        "topaz/upscale/image/creative",
        "topaz/upscale/image/generative",
        "topaz/upscale/image/precision",
        "topaz/upscale/image/transparent",
        "xai/grok-imagine-image/v2.0/edit",
        "xai/grok-imagine-image/v2.0/text-to-image",
        "xai/grok-imagine-video/v1.5/image-to-video",
        "xai/grok-imagine-video/v1.5/reference-to-video",
        "xai/grok-imagine-video/v1.5/text-to-video",
    }
)

_CONFIG_ADAPTER: TypeAdapter[Any] = TypeAdapter(FalConfig)


def _iter_config_classes() -> list[type[BaseFalConfig]]:
    union_type = get_args(FalConfig)[0] if get_origin(FalConfig) is Annotated else FalConfig
    return list(get_args(union_type))


def config_class_for_app_id(app_id: str) -> type[BaseFalConfig] | None:
    for config_class in _iter_config_classes():
        app_id_field = config_class.model_fields["app_id"]
        if app_id in get_args(app_id_field.annotation):
            return config_class
    return None


def parameter_field_is_list(app_id: str, field_name: str) -> bool | None:
    config_class = config_class_for_app_id(app_id)
    if config_class is None:
        return None
    field = config_class.model_fields.get(field_name)
    if field is None:
        raise ValueError(f"{field_name!r} is not a parameter for {app_id!r}")
    return _annotation_is_list(field.annotation)


def _annotation_is_list(annotation: Any) -> bool:
    origin = get_origin(annotation)
    if origin is Annotated:
        return _annotation_is_list(get_args(annotation)[0])
    if origin is list:
        return True
    if origin in (Union, UnionType):
        return any(_annotation_is_list(arg) for arg in get_args(annotation) if arg is not NoneType)
    return False


def validate_parameters(app_id: str, parameters: dict[str, Any]) -> BaseFalConfig | None:
    if app_id not in SUPPORTED_APP_IDS:
        warnings.warn(
            (
                f"app_id {app_id!r} is not registered; "
                "parameters will be passed through without validation"
            ),
            UserWarning,
            stacklevel=2,
        )
        return None
    return cast(BaseFalConfig, _CONFIG_ADAPTER.validate_python({"app_id": app_id, **parameters}))


def validate_job_schema(raw_payload: dict[str, Any]) -> JobConfig:
    return JobConfig.model_validate(raw_payload)


__all__ = [
    "BaseFalConfig",
    "BriaIncreaseResolutionConfig",
    "BriaVideoBackgroundRemovalGreenScreenDespillConfig",
    "BriaVideoOutputContainerAndCodec",
    "FalConfig",
    "Flux3EditVideoConfig",
    "Flux3ExtendVideoConfig",
    "Flux3FirstLastFrameToVideoConfig",
    "Flux3ImageToVideoConfig",
    "Flux3Keyframe",
    "Flux3KeyframesToVideoConfig",
    "Flux3TextToVideoConfig",
    "FluxVideoUpscaleConfig",
    "GeminiOmniFlashEditConfig",
    "GeminiOmniFlashImageToVideoConfig",
    "GeminiOmniFlashReferenceToVideoConfig",
    "GeminiOmniFlashTextToVideoConfig",
    "Gemini31FlashTtsConfig",
    "Gemini38FlashLiteTtsConfig",
    "Gemini38FlashTtsConfig",
    "Gemini38SpeechTurn",
    "Gemini38TtsSpeaker",
    "GeminiOmniFlashV11EditConfig",
    "GeminiOmniFlashV11ImageToVideoConfig",
    "GeminiOmniFlashV11ReferenceToVideoConfig",
    "GeminiOmniFlashV11TextToVideoConfig",
    "GeminiOmniFlashV12EditConfig",
    "GeminiOmniFlashV12ExtendConfig",
    "GeminiOmniFlashV12ImageToVideoConfig",
    "GeminiOmniFlashV12ReferenceToVideoConfig",
    "GeminiOmniFlashV12TextToVideoConfig",
    "GeminiOmniFlashV12UpscaleConfig",
    "GeminiTtsConfig",
    "GeminiTtsLanguage",
    "GeminiTtsSpeaker",
    "GeminiTtsVoice",
    "GptImage2Config",
    "GptImage2EditConfig",
    "GptImage25FlareEditConfig",
    "GptImage25FlareTextToImageConfig",
    "GptImage25SunburstEditConfig",
    "GptImage25SunburstTextToImageConfig",
    "GrokImagineImageV20AspectRatio",
    "GrokImagineImageV20BaseConfig",
    "GrokImagineImageV20EditAspectRatio",
    "GrokImagineImageV20EditConfig",
    "GrokImagineImageV20TextToImageConfig",
    "GrokImagineVideoV15AspectRatio",
    "GrokImagineVideoV15ImageToVideoConfig",
    "GrokImagineVideoV15ReferenceResolution",
    "GrokImagineVideoV15ReferenceToVideoConfig",
    "GrokImagineVideoV15Resolution",
    "GrokImagineVideoV15TextToVideoConfig",
    "H3MaxCameraKeyframe",
    "HappyHorseImageToVideoConfig",
    "HappyHorseReferenceToVideoConfig",
    "HappyHorseTextToVideoConfig",
    "HappyHorseVideoEditConfig",
    "IdeogramV4Config",
    "IdeogramV4ImageSize",
    "ImageSize",
    "JobConfig",
    "KlingO3ComboElementInput",
    "KlingO34kVideoToVideoAspectRatio",
    "KlingO3ImageElementInput",
    "KlingO3MultiPromptElement",
    "KlingVideoO34kImageToVideoConfig",
    "KlingVideoO34kReferenceToVideoConfig",
    "KlingVideoO34kTextToVideoConfig",
    "KlingVideoO34kVideoToVideoEditConfig",
    "KlingVideoO34kVideoToVideoReferenceConfig",
    "KlingVideoO3ProImageToVideoConfig",
    "KlingVideoO3ProReferenceToVideoConfig",
    "KlingVideoO3ProTextToVideoConfig",
    "KlingVideoO3ProVideoToVideoEditConfig",
    "KlingV3ComboElementInput",
    "KlingV3ImageElementInput",
    "KlingV3MultiPromptElement",
    "KlingVideoV34kImageToVideoConfig",
    "KlingVideoV34kTextToVideoConfig",
    "KlingVideoV3ProImageToVideoConfig",
    "KlingVideoV3ProMotionControlConfig",
    "KlingVideoV3ProTextToVideoConfig",
    "LumaRay32EditControls",
    "LumaRay32EditDepthControl",
    "LumaRay32EditFaceControl",
    "LumaRay32EditNormalsControl",
    "LumaRay32EditPoseControl",
    "LumaRay32EditTrajectoryControl",
    "LumaRay32ImageToVideoConfig",
    "LumaRay32ReframeConfig",
    "LumaRay32ReframeSourcePosition",
    "LumaRay32TextToVideoConfig",
    "LumaRay32VideoToVideoConfig",
    "Lyria2Config",
    "Lyria3Config",
    "Lyria3ProConfig",
    "Lyria35Config",
    "MatrixAxes",
    "MatrixAxis",
    "MeshyV7TextTo3dConfig",
    "MinimaxH3MaxCameraControlsConfig",
    "MinimaxH3MaxImageToVideoConfig",
    "MinimaxH3MaxReferenceToVideoConfig",
    "MinimaxH3MaxTextToVideoConfig",
    "MinimaxH3MaxTurboImageToVideoConfig",
    "MinimaxH3MaxTurboTextToVideoConfig",
    "MinimaxMusic3Config",
    "MuseImageAspectRatio",
    "MuseImageBaseConfig",
    "MuseImageEditConfig",
    "MuseImageTextToImageConfig",
    "NanoBanana2Config",
    "NanoBanana2EditConfig",
    "NanoBanana21Config",
    "NanoBanana21EditConfig",
    "NanoBananaConfig",
    "NanoBananaEditConfig",
    "NanoBananaLiteConfig",
    "NanoBananaLiteEditConfig",
    "NanoBananaProConfig",
    "NanoBananaProEditConfig",
    "QwenAudio3TtsConfig",
    "QwenImage3EditConfig",
    "QwenImage3ImageSize",
    "QwenImage3TextToImageConfig",
    "Sam31BoxPrompt",
    "Sam31BoxPromptBase",
    "Sam31ImageConfig",
    "Sam31ImageOutputFormat",
    "Sam31ImageRleConfig",
    "Sam31Label",
    "Sam31PointPrompt",
    "Sam31PointPromptBase",
    "Sam31VideoConfig",
    "Sam31VideoOutputType",
    "Sam31VideoRleConfig",
    "SeedreamV45EditConfig",
    "SeedreamV45ImageSize",
    "SeedreamV45TextToImageConfig",
    "SeedreamV5LiteEditConfig",
    "SeedreamV5LiteImageSize",
    "SeedreamV5LiteTextToImageConfig",
    "SeedreamV5ProEditConfig",
    "SeedreamV5ProImageSize",
    "SeedreamV5ProLayerizeConfig",
    "SeedreamV5ProTextToImageConfig",
    "Seedance2FastImageToVideoConfig",
    "Seedance2FastReferenceToVideoConfig",
    "Seedance2FastTextToVideoConfig",
    "Seedance2ImageToVideoConfig",
    "Seedance2MiniImageToVideoConfig",
    "Seedance2MiniReferenceToVideoConfig",
    "Seedance2MiniTextToVideoConfig",
    "Seedance2ReferenceToVideoConfig",
    "Seedance2TextToVideoConfig",
    "Seedance25ImageToVideoConfig",
    "Seedance25ReferenceToVideoConfig",
    "Seedance25TextToVideoConfig",
    "SoniloV11SfxSegment",
    "SoniloV11VideoToSoundEffectsConfig",
    "SUPPORTED_APP_IDS",
    "TopazDeblurVideoConfig",
    "TopazInterpolateVideoConfig",
    "TopazUpscaleImageCreativeConfig",
    "TopazUpscaleImageGenerativeConfig",
    "TopazUpscaleImagePrecisionConfig",
    "TopazUpscaleImageTransparentConfig",
    "Veo31ExtendVideoConfig",
    "Veo31FirstLastFrameToVideoConfig",
    "Veo31ImageToVideoConfig",
    "Veo31LiteFirstLastFrameToVideoConfig",
    "Veo31LiteImageToVideoConfig",
    "Veo31LiteTextToVideoConfig",
    "Veo31ReferenceToVideoConfig",
    "Veo31TextToVideoConfig",
    "Veo3ImageToVideoConfig",
    "Veo3TextToVideoConfig",
    "Vggt1bConfig",
    "ViduQ3ImageToVideoConfig",
    "ViduQ3ReferenceToVideoConfig",
    "ViduQ3ReferenceToVideoMixConfig",
    "ViduQ3TextToVideoConfig",
    "VirtualTryOnConfig",
    "Wan30PrimeImageToVideoConfig",
    "Wan30PrimeReferenceToVideoConfig",
    "Wan30PrimeTextToVideoConfig",
    "config_class_for_app_id",
    "parameter_field_is_list",
    "validate_job_schema",
    "validate_parameters",
]
