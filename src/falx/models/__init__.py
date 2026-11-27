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
    schema_example_parameters: ClassVar[dict[str, Any]] = {}


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
            raise ValueError("matrix axis field/values and fields/value_set are mutually exclusive")

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


from falx.models.bria_fibo_2_edit import BriaFibo2EditConfig  # noqa: E402
from falx.models.bria_fibo_2_generate import BriaFibo2GenerateConfig  # noqa: E402
from falx.models.bria_fibo_edit_1_5_expand import BriaFiboEdit15ExpandConfig  # noqa: E402
from falx.models.bria_guided_remove_background import (  # noqa: E402
    BriaGuidedRemoveBackgroundConfig,
)
from falx.models.bria_increase_resolution import BriaIncreaseResolutionConfig  # noqa: E402
from falx.models.bria_rmbg_3 import BriaRmbg3Config  # noqa: E402
from falx.models.bria_video_background_removal import (  # noqa: E402
    BriaVideoBackgroundRemovalConfig,
    BriaVideoBackgroundRemovalV3Config,
)
from falx.models.bria_video_background_removal_green_screen_despill import (  # noqa: E402
    BriaVideoBackgroundRemovalGreenScreenDespillConfig,
    BriaVideoOutputContainerAndCodec,
)
from falx.models.bria_video_erase import (  # noqa: E402
    BriaVideoEraseKeypointsConfig,
    BriaVideoEraseMaskConfig,
    BriaVideoEraseOutputContainerAndCodec,
    BriaVideoErasePromptConfig,
)
from falx.models.bria_video_increase_resolution import (  # noqa: E402
    BriaVideoIncreaseResolutionConfig,
)
from falx.models.elevenlabs_sound_effects_v3 import ElevenLabsSoundEffectsV3Config  # noqa: E402
from falx.models.flashvsr_plus import FlashvsrPlusConfig  # noqa: E402
from falx.models.flux_3_common import Flux3Keyframe  # noqa: E402
from falx.models.flux_3_draft_enhance import Flux3DraftEnhanceConfig  # noqa: E402
from falx.models.flux_3_edit_image import Flux3EditImageConfig  # noqa: E402
from falx.models.flux_3_edit_video import Flux3EditVideoConfig  # noqa: E402
from falx.models.flux_3_extend_video import Flux3ExtendVideoConfig  # noqa: E402
from falx.models.flux_3_extend_video_draft import Flux3ExtendVideoDraftConfig  # noqa: E402
from falx.models.flux_3_first_last_frame_to_video import (  # noqa: E402
    Flux3FirstLastFrameToVideoConfig,
)
from falx.models.flux_3_first_last_frame_to_video_draft import (  # noqa: E402
    Flux3FirstLastFrameToVideoDraftConfig,
)
from falx.models.flux_3_image_to_video import Flux3ImageToVideoConfig  # noqa: E402
from falx.models.flux_3_image_to_video_draft import Flux3ImageToVideoDraftConfig  # noqa: E402
from falx.models.flux_3_keyframes_to_video import (  # noqa: E402
    Flux3KeyframesToVideoConfig,
)
from falx.models.flux_3_keyframes_to_video_draft import (  # noqa: E402
    Flux3KeyframesToVideoDraftConfig,
)
from falx.models.flux_3_klein_common import (  # noqa: E402
    Flux3KleinBoundingBox,
    Flux3KleinBox,
    Flux3KleinEditBoundingBox,
    Flux3KleinImageSize,
    Flux3KleinLoRAInput,
)
from falx.models.flux_3_klein_edit_image import (  # noqa: E402
    Flux3KleinBaseEditImageLoraConfig,
    Flux3KleinEditImageConfig,
    Flux3KleinEditImageLoraConfig,
)
from falx.models.flux_3_klein_text_to_image import (  # noqa: E402
    Flux3KleinBaseTextToImageLoraConfig,
    Flux3KleinTextToImageConfig,
    Flux3KleinTextToImageLoraConfig,
)
from falx.models.flux_3_max_image_to_video import Flux3MaxImageToVideoConfig  # noqa: E402
from falx.models.flux_3_max_keyframes_to_video import (  # noqa: E402
    Flux3MaxKeyframesToVideoConfig,
)
from falx.models.flux_3_max_text_to_video import Flux3MaxTextToVideoConfig  # noqa: E402
from falx.models.flux_3_text_to_image import Flux3TextToImageConfig  # noqa: E402
from falx.models.flux_3_text_to_video import Flux3TextToVideoConfig  # noqa: E402
from falx.models.flux_3_text_to_video_draft import Flux3TextToVideoDraftConfig  # noqa: E402
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
from falx.models.gpt_image_2_6 import (  # noqa: E402
    GptImage26FlareTextToImageConfig,
    GptImage26SunburstTextToImageConfig,
)
from falx.models.gpt_image_2_6_edit import (  # noqa: E402
    GptImage26FlareEditConfig,
    GptImage26SunburstEditConfig,
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
from falx.models.grok_imagine_video_v1_5_lite_common import (  # noqa: E402
    GrokImagineVideoV15LiteKeyframe,
)
from falx.models.grok_imagine_video_v1_5_lite_image_to_video import (  # noqa: E402
    GrokImagineVideoV15LiteImageToVideoConfig,
)
from falx.models.grok_imagine_video_v1_5_lite_text_to_video import (  # noqa: E402
    GrokImagineVideoV15LiteTextToVideoConfig,
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
from falx.models.heygen_video_image_to_video import HeygenVideoImageToVideoConfig  # noqa: E402
from falx.models.heygen_video_reference_to_video import (  # noqa: E402
    HeygenVideoReferenceToVideoConfig,
)
from falx.models.heygen_video_text_to_video import HeygenVideoTextToVideoConfig  # noqa: E402
from falx.models.heygen_voice import HeygenVoiceConfig  # noqa: E402
from falx.models.hyper3d_lowpoly import (  # noqa: E402
    Hyper3dLowpolyImageTo3dConfig,
    Hyper3dLowpolyMeshTo3dConfig,
    Hyper3dLowpolyTextTo3dConfig,
)
from falx.models.hyper3d_rigging import (  # noqa: E402
    Hyper3dRiggingAnimationsConfig,
    Hyper3dRiggingConfig,
    Hyper3dRigHierarchyNode,
)
from falx.models.ideogram_v4 import (  # noqa: E402
    IdeogramV4Config,
    IdeogramV4ImageSize,
)
from falx.models.ideogram_v4_6 import (  # noqa: E402
    IdeogramV46Config,
    IdeogramV46ContextWindowBox,
    IdeogramV46EditConfig,
)
from falx.models.ideogram_v4_variants import (  # noqa: E402
    IdeogramV4FastConfig,
    IdeogramV4ImageToImageConfig,
    IdeogramV4ImageToImageLoraConfig,
    IdeogramV4InstantConfig,
    IdeogramV4LoraConfig,
    IdeogramV4LoRAInput,
    IdeogramV4TilingConfig,
    IdeogramV4TilingLoraConfig,
)
from falx.models.ideogram_vector import (  # noqa: E402
    IdeogramVectorImageToVectorConfig,
    IdeogramVectorTextToVectorConfig,
)
from falx.models.idol import IdolConfig, IdolMaxConfig  # noqa: E402
from falx.models.iris_z import (  # noqa: E402
    IrisZDepthConfig,
    IrisZDepthToImageConfig,
    IrisZImageSize,
    IrisZSmallDepthConfig,
    IrisZSmallDepthToImageConfig,
    IrisZSmallTextToImageConfig,
    IrisZSmallTextToRgbdConfig,
    IrisZTextToImageConfig,
    IrisZTextToRgbdConfig,
)
from falx.models.kandinsky6_pro_image_to_video import (  # noqa: E402
    Kandinsky6ProImageToVideoConfig,
)
from falx.models.kandinsky6_pro_text_to_video import (  # noqa: E402
    Kandinsky6ProTextToVideoConfig,
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
from falx.models.kling_o3_standard_image_to_video import (  # noqa: E402
    KlingVideoO3StandardImageToVideoConfig,
)
from falx.models.kling_o3_standard_reference_to_video import (  # noqa: E402
    KlingVideoO3StandardReferenceToVideoConfig,
)
from falx.models.kling_o3_standard_text_to_video import (  # noqa: E402
    KlingVideoO3StandardTextToVideoConfig,
)
from falx.models.kling_o3_standard_video_to_video_edit import (  # noqa: E402
    KlingVideoO3StandardVideoToVideoEditConfig,
)
from falx.models.kling_o3_video_to_video_reference import (  # noqa: E402
    KlingVideoO3VideoToVideoReferenceConfig,
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
from falx.models.kling_v3_standard_image_to_video import (  # noqa: E402
    KlingVideoV3StandardImageToVideoConfig,
)
from falx.models.kling_v3_standard_motion_control import (  # noqa: E402
    KlingVideoV3StandardMotionControlConfig,
)
from falx.models.kling_v3_standard_text_to_video import (  # noqa: E402
    KlingVideoV3StandardTextToVideoConfig,
)
from falx.models.kling_v3_turbo_image_to_video import (  # noqa: E402
    KlingVideoV3TurboImageToVideoConfig,
)
from falx.models.kling_v3_turbo_text_to_video import (  # noqa: E402
    KlingVideoV3TurboTextToVideoConfig,
)
from falx.models.kling_v4_common import (  # noqa: E402
    KlingV4Element,
    KlingV4FlashElement,
    KlingV4Shot,
)
from falx.models.kling_v4_flash_image_to_video import (  # noqa: E402
    KlingV4FlashImageToVideoConfig,
)
from falx.models.kling_v4_flash_reference_to_video import (  # noqa: E402
    KlingV4FlashReferenceToVideoConfig,
)
from falx.models.kling_v4_flash_text_to_video import (  # noqa: E402
    KlingV4FlashTextToVideoConfig,
)
from falx.models.kling_v4_flash_video_to_video import (  # noqa: E402
    KlingV4FlashVideoToVideoConfig,
)
from falx.models.kling_v4_image_common import KlingV4ImageElement  # noqa: E402
from falx.models.kling_v4_image_to_image import KlingV4ImageToImageConfig  # noqa: E402
from falx.models.kling_v4_image_to_video import (  # noqa: E402
    KlingV4ImageToVideoConfig,
)
from falx.models.kling_v4_long_image import KlingV4LongImageConfig  # noqa: E402
from falx.models.kling_v4_reference_to_video import (  # noqa: E402
    KlingV4ReferenceToVideoConfig,
)
from falx.models.kling_v4_text_to_image import KlingV4TextToImageConfig  # noqa: E402
from falx.models.kling_v4_text_to_video import (  # noqa: E402
    KlingV4TextToVideoConfig,
)
from falx.models.kling_v4_video_to_video_edit import (  # noqa: E402
    KlingV4VideoToVideoEditConfig,
)
from falx.models.kotoba_stt_v1_speech_to_text import (  # noqa: E402
    KotobaSttV1SpeechToTextConfig,
)
from falx.models.krea_3_common import Krea3ImageSize, Krea3LoRAInput  # noqa: E402
from falx.models.krea_3_edit import (  # noqa: E402
    Krea3EditConfig,
    Krea3EditLoraConfig,
    Krea3EditRegion,
)
from falx.models.krea_3_text_to_image import (  # noqa: E402
    Krea3TextToImageConfig,
    Krea3TextToImageLoraConfig,
)
from falx.models.ltx_2_5 import (  # noqa: E402
    Ltx25AlphaGenConfig,
    Ltx25HdrConfig,
    Ltx25ReframeAnchor,
    Ltx25ReframeConfig,
    Ltx25ReframeRectangle,
    Ltx25UpscaleConfig,
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
from falx.models.mai_image_2_7 import (  # noqa: E402
    MaiImage27FlashTextToImageConfig,
    MaiImage27ImageSize,
    MaiImage27TextToImageConfig,
)
from falx.models.mai_image_2_7_edit import (  # noqa: E402
    MaiImage27EditConfig,
    MaiImage27FlashEditConfig,
)
from falx.models.marigold_v2 import MarigoldV2Config, MarigoldV2ImageSize  # noqa: E402
from falx.models.meshy_relief import MeshyReliefConfig  # noqa: E402
from falx.models.meshy_retexture import (  # noqa: E402
    MeshyN1RetextureConfig,
    MeshyV6LiteRetextureConfig,
    MeshyV6RetextureConfig,
)
from falx.models.meshy_rigging import (  # noqa: E402
    MeshyRiggingConfig,
    MeshyRiggingMultiAnimationConfig,
)
from falx.models.meshy_smart_topology import (  # noqa: E402
    MeshyT2ImageTo3dConfig,
    MeshyT2TextTo3dConfig,
    MeshyT25ImageTo3dConfig,
    MeshyT25TextTo3dConfig,
)
from falx.models.meshy_v7_image_to_3d import (  # noqa: E402
    MeshyV7ImageTo3dConfig,
)
from falx.models.meshy_v7_retexture import (  # noqa: E402
    MeshyV7RetextureConfig,
)
from falx.models.meshy_v7_text_to_3d import MeshyV7TextTo3dConfig  # noqa: E402
from falx.models.minimax_h3_image import (  # noqa: E402
    MinimaxH3ImageHighspeedTextToImageConfig,
    MinimaxH3ImageTextToImageConfig,
)
from falx.models.minimax_h3_image_common import (  # noqa: E402
    H3ImageLoraInput,
    MinimaxH3ImageSize,
)
from falx.models.minimax_h3_image_edit import (  # noqa: E402
    MinimaxH3ImageEditConfig,
    MinimaxH3ImageHighspeedEditConfig,
)
from falx.models.minimax_h3_image_to_video import MinimaxH3ImageToVideoConfig  # noqa: E402
from falx.models.minimax_h3_lora import (  # noqa: E402
    H3LoraInput,
    MinimaxH3ImageToVideoLoraConfig,
    MinimaxH3ReferenceToVideoLoraConfig,
    MinimaxH3TextToVideoLoraConfig,
)
from falx.models.minimax_h3_max_3d_to_video import (  # noqa: E402
    MinimaxH3Max3dToVideoConfig,
)
from falx.models.minimax_h3_max_camera_controls import (  # noqa: E402
    H3MaxCameraKeyframe,
    MinimaxH3MaxCameraControlsConfig,
)
from falx.models.minimax_h3_max_extend_video import (  # noqa: E402
    MinimaxH3MaxExtendVideoConfig,
)
from falx.models.minimax_h3_max_image_to_video import (  # noqa: E402
    MinimaxH3MaxImageToVideoConfig,
)
from falx.models.minimax_h3_max_insert_video import (  # noqa: E402
    MinimaxH3MaxInsertVideoConfig,
)
from falx.models.minimax_h3_max_lip_sync_image_to_video import (  # noqa: E402
    MinimaxH3MaxLipSyncImageToVideoConfig,
)
from falx.models.minimax_h3_max_recast import MinimaxH3MaxRecastConfig  # noqa: E402
from falx.models.minimax_h3_max_reference_to_video import (  # noqa: E402
    MinimaxH3MaxReferenceToVideoConfig,
)
from falx.models.minimax_h3_max_reframe_video import (  # noqa: E402
    MinimaxH3MaxReframeVideoConfig,
)
from falx.models.minimax_h3_max_relight import MinimaxH3MaxRelightConfig  # noqa: E402
from falx.models.minimax_h3_max_text_to_video import (  # noqa: E402
    MinimaxH3MaxTextToVideoConfig,
)
from falx.models.minimax_h3_max_turbo_extend_video import (  # noqa: E402
    MinimaxH3MaxTurboExtendVideoConfig,
)
from falx.models.minimax_h3_max_turbo_image_to_video import (  # noqa: E402
    MinimaxH3MaxTurboImageToVideoConfig,
)
from falx.models.minimax_h3_max_turbo_reference_to_video import (  # noqa: E402
    H3MaxTurboReferenceCondition,
    MinimaxH3MaxTurboReferenceToVideoConfig,
)
from falx.models.minimax_h3_max_turbo_text_to_video import (  # noqa: E402
    MinimaxH3MaxTurboTextToVideoConfig,
)
from falx.models.minimax_h3_reference_to_video import (  # noqa: E402
    MinimaxH3ReferenceToVideoConfig,
)
from falx.models.minimax_h3_text_to_video import MinimaxH3TextToVideoConfig  # noqa: E402
from falx.models.minimax_music_3 import MinimaxMusic3Config  # noqa: E402
from falx.models.mirelo_sfx_2_0 import (  # noqa: E402
    MireloSfx20TextToAudioConfig,
    MireloSfx20VideoToAudioConfig,
    MireloSfx20VideoToVideoConfig,
)
from falx.models.mischief_1_image_to_video import Mischief1ImageToVideoConfig  # noqa: E402
from falx.models.moge import Moge2Config, Moge3Config  # noqa: E402
from falx.models.moss_image import MossImageConfig, MossImageSize  # noqa: E402
from falx.models.motion_to_code import (  # noqa: E402
    MotionToCodeGlslConfig,
    MotionToCodeGsapConfig,
)
from falx.models.mureka import (  # noqa: E402
    MurekaFilesUploadConfig,
    MurekaInstrumentalConfig,
    MurekaSongConfig,
    MurekaSongExtendConfig,
    MurekaSongRemixConfig,
    MurekaSoundtrackConfig,
    MurekaTrackConfig,
)
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
from falx.models.pixverse_v6_extend import PixverseV6ExtendConfig  # noqa: E402
from falx.models.pixverse_v6_max_image_to_video import (  # noqa: E402
    PixverseV6MaxImageToVideoConfig,
)
from falx.models.pixverse_v6_max_text_to_video import (  # noqa: E402
    PixverseV6MaxTextToVideoConfig,
)
from falx.models.pixverse_v6_transition import PixverseV6TransitionConfig  # noqa: E402
from falx.models.qwen_audio_3_tts import QwenAudio3TtsConfig  # noqa: E402
from falx.models.qwen_image_3_common import QwenImage3ImageSize  # noqa: E402
from falx.models.qwen_image_3_edit import QwenImage3EditConfig  # noqa: E402
from falx.models.qwen_image_3_text_to_image import (  # noqa: E402
    QwenImage3TextToImageConfig,
)
from falx.models.recraft_v4_1_flash_v2_text_to_image import (  # noqa: E402
    RecraftV41FlashV2ImageSize,
    RecraftV41FlashV2RGBColor,
    RecraftV41FlashV2TextToImageConfig,
)
from falx.models.recraft_vectorize_pro import RecraftVectorizeProConfig  # noqa: E402
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
from falx.models.seed_tts_v3 import SeedTtsV3Config  # noqa: E402
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
from falx.models.seedance2_us_image_to_video import (  # noqa: E402
    Seedance2UsImageToVideoConfig,
)
from falx.models.seedance2_us_reference_to_video import (  # noqa: E402
    Seedance2UsReferenceToVideoConfig,
)
from falx.models.seedance2_us_text_to_video import (  # noqa: E402
    Seedance2UsTextToVideoConfig,
)
from falx.models.seedance25_flash_image_to_video import (  # noqa: E402
    Seedance25FlashImageToVideoConfig,
)
from falx.models.seedance25_flash_reference_to_video import (  # noqa: E402
    Seedance25FlashReferenceToVideoConfig,
)
from falx.models.seedance25_flash_text_to_video import (  # noqa: E402
    Seedance25FlashTextToVideoConfig,
)
from falx.models.seedance25_image_to_video import Seedance25ImageToVideoConfig  # noqa: E402
from falx.models.seedance25_reference_to_video import (  # noqa: E402
    Seedance25ReferenceToVideoConfig,
)
from falx.models.seedance25_text_to_video import Seedance25TextToVideoConfig  # noqa: E402
from falx.models.seedance25_us_draft_complete import Seedance25UsDraftCompleteConfig  # noqa: E402
from falx.models.seedance25_us_image_to_video import (  # noqa: E402
    Seedance25UsImageToVideoConfig,
)
from falx.models.seedance25_us_reference_to_video import (  # noqa: E402
    Seedance25UsReferenceToVideoConfig,
)
from falx.models.seedance25_us_text_to_video import (  # noqa: E402
    Seedance25UsTextToVideoConfig,
)
from falx.models.seedream_v5_flash_edit import SeedreamV5FlashEditConfig  # noqa: E402
from falx.models.seedream_v5_flash_layerize import SeedreamV5FlashLayerizeConfig  # noqa: E402
from falx.models.seedream_v5_flash_text_to_image import (  # noqa: E402
    SeedreamV5FlashTextToImageConfig,
)
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
from falx.models.seedream_v5_pro_us_edit import SeedreamV5ProUsEditConfig  # noqa: E402
from falx.models.seedream_v5_pro_us_text_to_image import (  # noqa: E402
    SeedreamV5ProUsTextToImageConfig,
)
from falx.models.seedream_v45_edit import SeedreamV45EditConfig  # noqa: E402
from falx.models.seedream_v45_text_to_image import (  # noqa: E402
    SeedreamV45ImageSize,
    SeedreamV45TextToImageConfig,
)
from falx.models.seedream_v55_edit import SeedreamV55EditConfig  # noqa: E402
from falx.models.seedream_v55_layerize import SeedreamV55LayerizeConfig  # noqa: E402
from falx.models.seedream_v55_text_to_image import SeedreamV55TextToImageConfig  # noqa: E402
from falx.models.sonilo_v1_1_variants import (  # noqa: E402
    SoniloV11TextToMusicConfig,
    SoniloV11TextToSoundEffectsConfig,
    SoniloV11VideoToMusicConfig,
    SoniloV11VideoToVideoMusicConfig,
    SoniloV11VideoToVideoSoundEffectsConfig,
)
from falx.models.sonilo_v1_1_video_to_sound_effects import (  # noqa: E402
    SoniloV11SfxSegment,
    SoniloV11VideoToSoundEffectsConfig,
)
from falx.models.topaz_adjust_image import TopazAdjustImageConfig  # noqa: E402
from falx.models.topaz_deblur_video import TopazDeblurVideoConfig  # noqa: E402
from falx.models.topaz_denoise_image import TopazDenoiseImageConfig  # noqa: E402
from falx.models.topaz_denoise_video import TopazDenoiseVideoConfig  # noqa: E402
from falx.models.topaz_interpolate_video import TopazInterpolateVideoConfig  # noqa: E402
from falx.models.topaz_restore_image import TopazRestoreImageConfig  # noqa: E402
from falx.models.topaz_sdr_to_hdr_video import TopazSdrToHdrVideoConfig  # noqa: E402
from falx.models.topaz_sharpen_image import TopazSharpenImageConfig  # noqa: E402
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
from falx.models.topaz_upscale_video_creative import (  # noqa: E402
    TopazUpscaleVideoCreativeConfig,
)
from falx.models.topaz_upscale_video_generative import (  # noqa: E402
    TopazUpscaleVideoGenerativeConfig,
)
from falx.models.topaz_upscale_video_precision import (  # noqa: E402
    TopazUpscaleVideoPrecisionConfig,
)
from falx.models.veed_dubbing import VeedDubbingConfig, VeedDubbingProConfig  # noqa: E402
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
from falx.models.vidu_q3_image_to_video_turbo import (  # noqa: E402
    ViduQ3ImageToVideoTurboConfig,
)
from falx.models.vidu_q3_reference_to_video import (  # noqa: E402
    ViduQ3ReferenceToVideoConfig,
)
from falx.models.vidu_q3_reference_to_video_mix import (  # noqa: E402
    ViduQ3ReferenceToVideoMixConfig,
)
from falx.models.vidu_q3_text_to_video import ViduQ3TextToVideoConfig  # noqa: E402
from falx.models.vidu_q3_text_to_video_turbo import (  # noqa: E402
    ViduQ3TextToVideoTurboConfig,
)
from falx.models.vidu_q4_image_to_video import ViduQ4ImageToVideoConfig  # noqa: E402
from falx.models.vidu_q4_reference_to_video import (  # noqa: E402
    ViduQ4ReferenceToVideoConfig,
)
from falx.models.virtual_try_on import VirtualTryOnConfig  # noqa: E402
from falx.models.wan_3_0_image_to_video import (  # noqa: E402
    Wan30ImageToVideoConfig,
)
from falx.models.wan_3_0_prime_image_to_video import (  # noqa: E402
    Wan30PrimeImageToVideoConfig,
)
from falx.models.wan_3_0_prime_reference_to_video import (  # noqa: E402
    Wan30PrimeReferenceToVideoConfig,
)
from falx.models.wan_3_0_prime_text_to_video import (  # noqa: E402
    Wan30PrimeTextToVideoConfig,
)
from falx.models.wan_3_0_reference_to_video import (  # noqa: E402
    Wan30ReferenceToVideoConfig,
)
from falx.models.wan_3_0_text_to_video import (  # noqa: E402
    Wan30TextToVideoConfig,
)

FalConfig = Annotated[
    BriaFibo2EditConfig
    | BriaFibo2GenerateConfig
    | BriaFiboEdit15ExpandConfig
    | BriaGuidedRemoveBackgroundConfig
    | BriaIncreaseResolutionConfig
    | BriaRmbg3Config
    | BriaVideoBackgroundRemovalConfig
    | BriaVideoBackgroundRemovalV3Config
    | BriaVideoBackgroundRemovalGreenScreenDespillConfig
    | BriaVideoEraseKeypointsConfig
    | BriaVideoEraseMaskConfig
    | BriaVideoErasePromptConfig
    | BriaVideoIncreaseResolutionConfig
    | FlashvsrPlusConfig
    | ElevenLabsSoundEffectsV3Config
    | MotionToCodeGlslConfig
    | MotionToCodeGsapConfig
    | VeedDubbingConfig
    | VeedDubbingProConfig
    | Flux3DraftEnhanceConfig
    | Flux3EditImageConfig
    | Flux3EditVideoConfig
    | Flux3ExtendVideoConfig
    | Flux3ExtendVideoDraftConfig
    | Flux3FirstLastFrameToVideoConfig
    | Flux3FirstLastFrameToVideoDraftConfig
    | Flux3ImageToVideoConfig
    | Flux3ImageToVideoDraftConfig
    | Flux3KeyframesToVideoConfig
    | Flux3MaxImageToVideoConfig
    | Flux3MaxKeyframesToVideoConfig
    | Flux3MaxTextToVideoConfig
    | Flux3KeyframesToVideoDraftConfig
    | Flux3KleinBaseEditImageLoraConfig
    | Flux3KleinBaseTextToImageLoraConfig
    | Flux3KleinEditImageConfig
    | Flux3KleinEditImageLoraConfig
    | Flux3KleinTextToImageConfig
    | Flux3KleinTextToImageLoraConfig
    | Flux3TextToImageConfig
    | Flux3TextToVideoConfig
    | Flux3TextToVideoDraftConfig
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
    | GptImage26FlareTextToImageConfig
    | GptImage26SunburstTextToImageConfig
    | GptImage26FlareEditConfig
    | GptImage26SunburstEditConfig
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
    | GrokImagineVideoV15LiteImageToVideoConfig
    | GrokImagineVideoV15LiteTextToVideoConfig
    | GrokImagineVideoV15ReferenceToVideoConfig
    | GrokImagineVideoV15TextToVideoConfig
    | HappyHorseImageToVideoConfig
    | HappyHorseReferenceToVideoConfig
    | HappyHorseTextToVideoConfig
    | HappyHorseVideoEditConfig
    | HeygenVideoImageToVideoConfig
    | HeygenVideoReferenceToVideoConfig
    | HeygenVideoTextToVideoConfig
    | HeygenVoiceConfig
    | IdeogramV4Config
    | Kandinsky6ProImageToVideoConfig
    | Kandinsky6ProTextToVideoConfig
    | IdeogramV4FastConfig
    | IdeogramV4ImageToImageConfig
    | IdeogramV4ImageToImageLoraConfig
    | IdeogramV4InstantConfig
    | IdeogramV4LoraConfig
    | IdeogramV4TilingConfig
    | IdeogramV4TilingLoraConfig
    | IdeogramV46Config
    | IdeogramV46EditConfig
    | IdeogramVectorImageToVectorConfig
    | IdeogramVectorTextToVectorConfig
    | IrisZDepthConfig
    | IrisZDepthToImageConfig
    | IrisZSmallDepthConfig
    | IrisZSmallDepthToImageConfig
    | IrisZSmallTextToImageConfig
    | IrisZSmallTextToRgbdConfig
    | IrisZTextToImageConfig
    | IrisZTextToRgbdConfig
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
    | KlingV4FlashImageToVideoConfig
    | KlingV4FlashReferenceToVideoConfig
    | KlingV4FlashTextToVideoConfig
    | KlingV4FlashVideoToVideoConfig
    | KlingV4ImageToImageConfig
    | KlingV4LongImageConfig
    | KlingV4TextToImageConfig
    | KlingV4ImageToVideoConfig
    | KlingV4ReferenceToVideoConfig
    | KlingV4TextToVideoConfig
    | KlingV4VideoToVideoEditConfig
    | KlingVideoO3StandardTextToVideoConfig
    | KlingVideoO3StandardImageToVideoConfig
    | KlingVideoO3StandardReferenceToVideoConfig
    | KlingVideoO3StandardVideoToVideoEditConfig
    | KlingVideoO3VideoToVideoReferenceConfig
    | KlingVideoV3StandardTextToVideoConfig
    | KlingVideoV3StandardImageToVideoConfig
    | KlingVideoV3StandardMotionControlConfig
    | KlingVideoV3TurboTextToVideoConfig
    | KlingVideoV3TurboImageToVideoConfig
    | Krea3EditConfig
    | Krea3EditLoraConfig
    | Krea3TextToImageConfig
    | Krea3TextToImageLoraConfig
    | Ltx25AlphaGenConfig
    | Ltx25HdrConfig
    | Ltx25ReframeConfig
    | Ltx25UpscaleConfig
    | LumaRay32ImageToVideoConfig
    | LumaRay32ReframeConfig
    | LumaRay32TextToVideoConfig
    | LumaRay32VideoToVideoConfig
    | KotobaSttV1SpeechToTextConfig
    | Lyria2Config
    | Lyria3Config
    | Lyria3ProConfig
    | Lyria35Config
    | MeshyN1RetextureConfig
    | MeshyReliefConfig
    | MeshyRiggingConfig
    | MeshyRiggingMultiAnimationConfig
    | MeshyT2ImageTo3dConfig
    | MeshyT2TextTo3dConfig
    | MeshyT25ImageTo3dConfig
    | MeshyT25TextTo3dConfig
    | MeshyV6LiteRetextureConfig
    | MeshyV6RetextureConfig
    | MaiImage27EditConfig
    | MaiImage27FlashEditConfig
    | MaiImage27FlashTextToImageConfig
    | MaiImage27TextToImageConfig
    | Hyper3dLowpolyImageTo3dConfig
    | Hyper3dLowpolyMeshTo3dConfig
    | Hyper3dLowpolyTextTo3dConfig
    | Hyper3dRiggingAnimationsConfig
    | Hyper3dRiggingConfig
    | MarigoldV2Config
    | MeshyV7ImageTo3dConfig
    | MeshyV7RetextureConfig
    | MeshyV7TextTo3dConfig
    | Moge2Config
    | Moge3Config
    | IdolConfig
    | IdolMaxConfig
    | MinimaxH3ImageEditConfig
    | MinimaxH3ImageHighspeedEditConfig
    | MinimaxH3ImageHighspeedTextToImageConfig
    | MinimaxH3ImageTextToImageConfig
    | MinimaxH3Max3dToVideoConfig
    | MinimaxH3ImageToVideoConfig
    | MinimaxH3ImageToVideoLoraConfig
    | MinimaxH3MaxCameraControlsConfig
    | MinimaxH3MaxExtendVideoConfig
    | MinimaxH3MaxImageToVideoConfig
    | MinimaxH3MaxInsertVideoConfig
    | MinimaxH3MaxLipSyncImageToVideoConfig
    | MinimaxH3MaxRecastConfig
    | MinimaxH3MaxReferenceToVideoConfig
    | MinimaxH3MaxReframeVideoConfig
    | MinimaxH3MaxRelightConfig
    | MinimaxH3MaxTextToVideoConfig
    | MinimaxH3MaxTurboExtendVideoConfig
    | MinimaxH3MaxTurboImageToVideoConfig
    | MinimaxH3MaxTurboReferenceToVideoConfig
    | MinimaxH3MaxTurboTextToVideoConfig
    | MinimaxH3ReferenceToVideoConfig
    | MinimaxH3ReferenceToVideoLoraConfig
    | MinimaxH3TextToVideoConfig
    | MinimaxH3TextToVideoLoraConfig
    | MinimaxMusic3Config
    | MireloSfx20TextToAudioConfig
    | MireloSfx20VideoToAudioConfig
    | MireloSfx20VideoToVideoConfig
    | Mischief1ImageToVideoConfig
    | MossImageConfig
    | MurekaFilesUploadConfig
    | MurekaInstrumentalConfig
    | MurekaSongConfig
    | MurekaSongExtendConfig
    | MurekaSongRemixConfig
    | MurekaSoundtrackConfig
    | MurekaTrackConfig
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
    | PixverseV6ExtendConfig
    | PixverseV6MaxImageToVideoConfig
    | PixverseV6MaxTextToVideoConfig
    | PixverseV6TransitionConfig
    | QwenAudio3TtsConfig
    | QwenImage3EditConfig
    | QwenImage3TextToImageConfig
    | RecraftV41FlashV2TextToImageConfig
    | RecraftVectorizeProConfig
    | Sam31ImageConfig
    | Sam31ImageRleConfig
    | Sam31VideoConfig
    | Sam31VideoRleConfig
    | SeedTtsV3Config
    | SeedreamV45EditConfig
    | SeedreamV45TextToImageConfig
    | SeedreamV5FlashEditConfig
    | SeedreamV5FlashLayerizeConfig
    | SeedreamV5FlashTextToImageConfig
    | SeedreamV5LiteEditConfig
    | SeedreamV5LiteTextToImageConfig
    | SeedreamV5ProEditConfig
    | SeedreamV5ProLayerizeConfig
    | SeedreamV5ProTextToImageConfig
    | SeedreamV5ProUsEditConfig
    | SeedreamV5ProUsTextToImageConfig
    | SeedreamV55EditConfig
    | SeedreamV55LayerizeConfig
    | SeedreamV55TextToImageConfig
    | Seedance2FastImageToVideoConfig
    | Seedance2FastReferenceToVideoConfig
    | Seedance2FastTextToVideoConfig
    | Seedance2ImageToVideoConfig
    | Seedance2MiniImageToVideoConfig
    | Seedance2MiniReferenceToVideoConfig
    | Seedance2MiniTextToVideoConfig
    | Seedance2ReferenceToVideoConfig
    | Seedance2TextToVideoConfig
    | Seedance25FlashImageToVideoConfig
    | Seedance25FlashReferenceToVideoConfig
    | Seedance25FlashTextToVideoConfig
    | Seedance2UsImageToVideoConfig
    | Seedance2UsReferenceToVideoConfig
    | Seedance2UsTextToVideoConfig
    | Seedance25ImageToVideoConfig
    | Seedance25ReferenceToVideoConfig
    | Seedance25TextToVideoConfig
    | Seedance25UsDraftCompleteConfig
    | Seedance25UsImageToVideoConfig
    | Seedance25UsReferenceToVideoConfig
    | Seedance25UsTextToVideoConfig
    | SoniloV11VideoToSoundEffectsConfig
    | TopazAdjustImageConfig
    | SoniloV11TextToMusicConfig
    | SoniloV11TextToSoundEffectsConfig
    | SoniloV11VideoToMusicConfig
    | SoniloV11VideoToVideoMusicConfig
    | SoniloV11VideoToVideoSoundEffectsConfig
    | TopazDeblurVideoConfig
    | TopazDenoiseImageConfig
    | TopazDenoiseVideoConfig
    | TopazInterpolateVideoConfig
    | TopazRestoreImageConfig
    | TopazSdrToHdrVideoConfig
    | TopazSharpenImageConfig
    | TopazUpscaleImageCreativeConfig
    | TopazUpscaleImageGenerativeConfig
    | TopazUpscaleImagePrecisionConfig
    | TopazUpscaleImageTransparentConfig
    | TopazUpscaleVideoCreativeConfig
    | TopazUpscaleVideoGenerativeConfig
    | TopazUpscaleVideoPrecisionConfig
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
    | ViduQ3ImageToVideoTurboConfig
    | ViduQ3ImageToVideoConfig
    | ViduQ3ReferenceToVideoConfig
    | ViduQ3ReferenceToVideoMixConfig
    | ViduQ3TextToVideoTurboConfig
    | ViduQ3TextToVideoConfig
    | ViduQ4ImageToVideoConfig
    | ViduQ4ReferenceToVideoConfig
    | VirtualTryOnConfig
    | Wan30ImageToVideoConfig
    | Wan30PrimeImageToVideoConfig
    | Wan30ReferenceToVideoConfig
    | Wan30PrimeReferenceToVideoConfig
    | Wan30TextToVideoConfig
    | Wan30PrimeTextToVideoConfig,
    Discriminator("app_id"),
]

SUPPORTED_APP_IDS = frozenset(
    {
        "krea/v3/edit",
        "krea/v3/edit/lora",
        "krea/v3/text-to-image",
        "krea/v3/text-to-image/lora",
        "speridlabs/iris-z",
        "speridlabs/iris-z/depth-to-image",
        "speridlabs/iris-z/small",
        "speridlabs/iris-z/small/depth-to-image",
        "speridlabs/iris-z/small/text-to-image",
        "speridlabs/iris-z/small/text-to-rgbd",
        "speridlabs/iris-z/text-to-image",
        "speridlabs/iris-z/text-to-rgbd",
        "lightricks/ltx-2.5/alpha-gen",
        "lightricks/ltx-2.5/hdr",
        "lightricks/ltx-2.5/reframe",
        "lightricks/ltx-2.5/upscale",
        "openimaginglab/flashvsr-plus",
        "fal-ai/motion-to-code/glsl",
        "fal-ai/motion-to-code/gsap",
        "veed/dubbing",
        "veed/dubbing/pro",
        "bria/fibo-2/edit",
        "bria/fibo-2/generate",
        "bria/fibo-edit-1.5/expand",
        "bria/guided-remove-background",
        "bria/rmbg-3",
        "fal-ai/gemini-tts",
        "fal-ai/marigold-v2",
        "fal-ai/moss-image",
        "recraft/v4.1/flash/v2/text-to-image",
        "recraft/vectorize/pro",
        "fal-ai/gemini-3.1-flash-tts",
        "google/gemini-3.8-flash-tts",
        "google/gemini-3.8-flash-lite-tts",
        "fal-ai/lyria2",
        "fal-ai/lyria3",
        "fal-ai/lyria3/pro",
        "google/lyria-3.5",
        "elevenlabs/sound-effects/v3",
        "mirelo-ai/sfx2.0/text-to-audio",
        "mirelo-ai/sfx2.0/video-to-audio",
        "mirelo-ai/sfx2.0/video-to-video",
        "google/virtual-try-on",
        "bytedance/seed-tts/v3",
        "heygen/heygen-voice",
        "heygen/heygen-voice/turbo",
        "kotoba-technologies/kotoba-stt/v1/speech-to-text",
        "alibaba/happy-horse/image-to-video",
        "alibaba/happy-horse/reference-to-video",
        "alibaba/happy-horse/text-to-video",
        "alibaba/happy-horse/video-edit",
        "alibaba/qwen-audio-3-tts",
        "alibaba/qwen-image-3/edit",
        "alibaba/qwen-image-3/text-to-image",
        "alibaba/wan-3.0/image-to-video",
        "alibaba/wan-3.0/reference-to-video",
        "alibaba/wan-3.0/text-to-video",
        "alibaba/wan-3.0-prime/image-to-video",
        "alibaba/wan-3.0-prime/reference-to-video",
        "alibaba/wan-3.0-prime/text-to-video",
        "blackforestlabs/flux-3/extend-video",
        "blackforestlabs/flux-3/edit-video",
        "blackforestlabs/flux-3/first-last-frame-to-video",
        "blackforestlabs/flux-3/image-to-video",
        "blackforestlabs/flux-3/keyframes-to-video",
        "blackforestlabs/flux-3/text-to-video",
        "blackforestlabs/flux-3-max/text-to-video",
        "blackforestlabs/flux-3-max/image-to-video",
        "blackforestlabs/flux-3-max/keyframes-to-video",
        "blackforestlabs/flux-3/text-to-video/draft",
        "blackforestlabs/flux-3/image-to-video/draft",
        "blackforestlabs/flux-3/first-last-frame-to-video/draft",
        "blackforestlabs/flux-3/keyframes-to-video/draft",
        "blackforestlabs/flux-3/extend-video/draft",
        "blackforestlabs/flux-3/draft-enhance",
        "blackforestlabs/flux-3/text-to-image",
        "blackforestlabs/flux-3/edit-image",
        "blackforestlabs/flux-3/klein/text-to-image",
        "blackforestlabs/flux-3/klein/edit-image",
        "blackforestlabs/flux-3/klein/text-to-image/lora",
        "blackforestlabs/flux-3/klein/edit-image/lora",
        "blackforestlabs/flux-3/klein/base/text-to-image/lora",
        "blackforestlabs/flux-3/klein/base/edit-image/lora",
        "blackforestlabs/flux-video-upscale",
        "bria/increase-resolution",
        "bria/video/background-removal",
        "bria/video/background-removal/v3",
        "bria/video/background-removal/green-screen-despill",
        "bria/video/erase/keypoints",
        "bria/video/erase/mask",
        "bria/video/erase/prompt",
        "bria/video/increase-resolution",
        "bytedance/seedance-2.0/fast/image-to-video",
        "bytedance/seedance-2.0/fast/reference-to-video",
        "bytedance/seedance-2.0/fast/text-to-video",
        "bytedance/seedance-2.0/image-to-video",
        "bytedance/seedance-2.0/mini/image-to-video",
        "bytedance/seedance-2.0/mini/reference-to-video",
        "bytedance/seedance-2.0/mini/text-to-video",
        "bytedance/seedance-2.0/reference-to-video",
        "bytedance/seedance-2.0/text-to-video",
        "bytedance/seedance-2.5/flash/image-to-video",
        "bytedance/seedance-2.5/flash/reference-to-video",
        "bytedance/seedance-2.5/flash/text-to-video",
        "bytedance/seedance-2.0/us/image-to-video",
        "bytedance/seedance-2.0/us/reference-to-video",
        "bytedance/seedance-2.0/us/text-to-video",
        "bytedance/seedance-2.5/image-to-video",
        "bytedance/seedance-2.5/reference-to-video",
        "bytedance/seedance-2.5/text-to-video",
        "bytedance/seedance-2.5/us/draft/complete",
        "bytedance/seedance-2.5/us/image-to-video",
        "bytedance/seedance-2.5/us/reference-to-video",
        "bytedance/seedance-2.5/us/text-to-video",
        "bytedance/seedream/v5/pro/edit",
        "bytedance/seedream/v5/pro/layerize",
        "bytedance/seedream/v5/pro/text-to-image",
        "bytedance/seedream/v5/flash/edit",
        "bytedance/seedream/v5/flash/layerize",
        "bytedance/seedream/v5/flash/text-to-image",
        "bytedance/seedream/v5/lite/edit",
        "bytedance/seedream/v5/lite/text-to-image",
        "bytedance/seedream/v5/pro/us/edit",
        "bytedance/seedream/v5/pro/us/text-to-image",
        "bytedance/seedream/v5.5/edit",
        "bytedance/seedream/v5.5/layerize",
        "bytedance/seedream/v5.5/text-to-image",
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
        "fal-ai/kling-video/o3/standard/text-to-video",
        "fal-ai/kling-video/o3/standard/image-to-video",
        "fal-ai/kling-video/o3/standard/reference-to-video",
        "fal-ai/kling-video/o3/standard/video-to-video/edit",
        "fal-ai/kling-video/o3/standard/video-to-video/reference",
        "fal-ai/kling-video/o3/pro/video-to-video/reference",
        "fal-ai/kling-video/v3/standard/text-to-video",
        "fal-ai/kling-video/v3/standard/image-to-video",
        "fal-ai/kling-video/v3/standard/motion-control",
        "fal-ai/kling-video/v3/turbo/standard/text-to-video",
        "fal-ai/kling-video/v3/turbo/standard/image-to-video",
        "fal-ai/kling-video/v3/turbo/pro/text-to-video",
        "fal-ai/kling-video/v3/turbo/pro/image-to-video",
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
        "heygen/heygen-video/text-to-video",
        "heygen/heygen-video/image-to-video",
        "heygen/heygen-video/reference-to-video",
        "ideogram/v4/fast",
        "ideogram/v4/image-to-image",
        "ideogram/v4/image-to-image/lora",
        "ideogram/v4/instant",
        "ideogram/v4/lora",
        "ideogram/v4/tiling",
        "ideogram/v4/tiling/lora",
        "ideogram/v4.6",
        "ideogram/v4.6/edit",
        "ideogram/vector/image-to-vector",
        "ideogram/vector/text-to-vector",
        "openai/gpt-image-2",
        "openai/gpt-image-2/edit",
        "openai/gpt-image-2.5/flare/edit",
        "openai/gpt-image-2.5/flare/text-to-image",
        "openai/gpt-image-2.5/sunburst/edit",
        "openai/gpt-image-2.5/sunburst/text-to-image",
        "openai/gpt-image-2.6/flare/edit",
        "openai/gpt-image-2.6/flare/text-to-image",
        "openai/gpt-image-2.6/sunburst/edit",
        "openai/gpt-image-2.6/sunburst/text-to-image",
        "topaz/adjust/image",
        "topaz/deblur/video",
        "tbc/mischief-1/image-to-video",
        "topaz/denoise/image",
        "topaz/denoise/video",
        "topaz/interpolate/video",
        "topaz/restore/image",
        "topaz/sdr-to-hdr/video",
        "topaz/sharpen/image",
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
        "fal-ai/kandinsky6-pro/image-to-video",
        "fal-ai/kandinsky6-pro/text-to-video",
        "fal-ai/vidu/q3/image-to-video",
        "fal-ai/vidu/q3/image-to-video/turbo",
        "fal-ai/vidu/q3/reference-to-video",
        "fal-ai/vidu/q3/reference-to-video/mix",
        "fal-ai/vidu/q3/text-to-video/turbo",
        "fal-ai/vidu/q3/text-to-video",
        "kling/v4/flash/image-to-video",
        "kling/v4/flash/reference-to-video",
        "kling/v4/flash/text-to-video",
        "kling/v4/flash/video-to-video",
        "kling/v4/image-to-image",
        "kling/v4/long-image",
        "kling/v4/text-to-image",
        "kling/v4/image-to-video",
        "kling/v4/reference-to-video",
        "kling/v4/text-to-video",
        "kling/v4/video-to-video/edit",
        "fal-ai/vidu/q4/image-to-video",
        "fal-ai/vidu/q4/reference-to-video",
        "luma/agent/ray/v3.2/image-to-video",
        "luma/agent/ray/v3.2/reframe",
        "luma/agent/ray/v3.2/text-to-video",
        "luma/agent/ray/v3.2/video-to-video",
        "meshy/n1/retexture",
        "meshy/relief",
        "meshy/rigging",
        "meshy/rigging/multi-animation",
        "meshy/t2/image-to-3d",
        "meshy/t2/text-to-3d",
        "meshy/t2.5/image-to-3d",
        "meshy/t2.5/text-to-3d",
        "meshy/v6/retexture",
        "meshy/v6-lite/retexture",
        "hyper3d/lowpoly/image-to-3d",
        "hyper3d/lowpoly/mesh-to-3d",
        "hyper3d/lowpoly/text-to-3d",
        "hyper3d/rigging/animations",
        "hyper3d/rigging",
        "meshy/v7/image-to-3d",
        "meshy/v7/retexture",
        "meshy/v7/text-to-3d",
        "microsoft/moge-2",
        "microsoft/moge-3",
        "speridlabs/idol",
        "speridlabs/idol/max",
        "speridlabs/idol/max/turbo",
        "minimax/h3-image/edit",
        "minimax/h3-image/highspeed/edit",
        "minimax/h3-image/highspeed/text-to-image",
        "minimax/h3-image/text-to-image",
        "minimax/h3-max/3d-to-video",
        "minimax/h3/image-to-video",
        "minimax/h3/image-to-video/lora",
        "minimax/h3/reference-to-video",
        "minimax/h3/reference-to-video/lora",
        "minimax/h3/text-to-video",
        "minimax/h3/text-to-video/lora",
        "minimax/h3-max/camera-controls",
        "minimax/h3-max/extend-video",
        "minimax/h3-max/image-to-video",
        "minimax/h3-max/insert-video",
        "minimax/h3-max/lip-sync/image-to-video",
        "minimax/h3-max/recast",
        "minimax/h3-max/reference-to-video",
        "minimax/h3-max/reframe-video",
        "minimax/h3-max/relight",
        "minimax/h3-max/text-to-video",
        "minimax/h3-max-turbo/extend-video",
        "minimax/h3-max-turbo/image-to-video",
        "minimax/h3-max-turbo/reference-to-video",
        "minimax/h3-max-turbo/text-to-video",
        "minimax/music-3",
        "mureka/api/files/upload",
        "mureka/v8/generate/instrumental",
        "mureka/v8/generate/song",
        "mureka/v8/generate/soundtrack",
        "mureka/v8/generate/track",
        "mureka/v8/song/extend",
        "mureka/v8/song/remix",
        "mureka/v9/generate/instrumental",
        "mureka/v9/generate/song",
        "mureka/v9/generate/soundtrack",
        "meta/muse-image/edit",
        "meta/muse-image/text-to-image",
        "microsoft/mai-image-2.7/edit",
        "microsoft/mai-image-2.7/flash/edit",
        "microsoft/mai-image-2.7/flash/text-to-image",
        "microsoft/mai-image-2.7/text-to-image",
        "sonilo/v1.1/video-to-sound-effects",
        "pixverse/v6/max/image-to-video",
        "pixverse/v6/max/text-to-video",
        "fal-ai/pixverse/v6/text-to-video",
        "fal-ai/pixverse/v6/image-to-video",
        "fal-ai/pixverse/v6/extend",
        "fal-ai/pixverse/v6/transition",
        "sonilo/v1.1/text-to-music",
        "sonilo/v1.1/text-to-sound-effects",
        "sonilo/v1.1/video-to-music",
        "sonilo/v1.1/video-to-video-music",
        "sonilo/v1.1/video-to-video-sound-effects",
        "topaz/upscale/image/creative",
        "topaz/upscale/image/generative",
        "topaz/upscale/image/precision",
        "topaz/upscale/image/transparent",
        "topaz/upscale/video/creative",
        "topaz/upscale/video/generative",
        "topaz/upscale/video/precision",
        "xai/grok-imagine-image/v2.0/edit",
        "xai/grok-imagine-image/v2.0/text-to-image",
        "xai/grok-imagine-video/v1.5/image-to-video",
        "xai/grok-imagine-video/v1.5/lite/text-to-video",
        "xai/grok-imagine-video/v1.5/lite/image-to-video",
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
    "MotionToCodeGlslConfig",
    "MotionToCodeGsapConfig",
    "VeedDubbingConfig",
    "VeedDubbingProConfig",
    "BaseFalConfig",
    "BriaFibo2EditConfig",
    "BriaFibo2GenerateConfig",
    "BriaFiboEdit15ExpandConfig",
    "BriaGuidedRemoveBackgroundConfig",
    "BriaIncreaseResolutionConfig",
    "BriaRmbg3Config",
    "BriaVideoBackgroundRemovalConfig",
    "BriaVideoBackgroundRemovalV3Config",
    "BriaVideoBackgroundRemovalGreenScreenDespillConfig",
    "BriaVideoEraseKeypointsConfig",
    "BriaVideoEraseMaskConfig",
    "BriaVideoEraseOutputContainerAndCodec",
    "BriaVideoErasePromptConfig",
    "BriaVideoIncreaseResolutionConfig",
    "BriaVideoOutputContainerAndCodec",
    "FalConfig",
    "FlashvsrPlusConfig",
    "ElevenLabsSoundEffectsV3Config",
    "MireloSfx20TextToAudioConfig",
    "MireloSfx20VideoToAudioConfig",
    "MireloSfx20VideoToVideoConfig",
    "Flux3DraftEnhanceConfig",
    "Flux3EditImageConfig",
    "Flux3EditVideoConfig",
    "Flux3ExtendVideoConfig",
    "Flux3ExtendVideoDraftConfig",
    "Flux3FirstLastFrameToVideoConfig",
    "Flux3FirstLastFrameToVideoDraftConfig",
    "Flux3ImageToVideoConfig",
    "Flux3ImageToVideoDraftConfig",
    "Flux3Keyframe",
    "Flux3KeyframesToVideoConfig",
    "Flux3MaxImageToVideoConfig",
    "Flux3MaxKeyframesToVideoConfig",
    "Flux3MaxTextToVideoConfig",
    "Flux3KeyframesToVideoDraftConfig",
    "Flux3KleinBaseEditImageLoraConfig",
    "Flux3KleinBaseTextToImageLoraConfig",
    "Flux3KleinBoundingBox",
    "Flux3KleinBox",
    "Flux3KleinEditBoundingBox",
    "Flux3KleinEditImageConfig",
    "Flux3KleinEditImageLoraConfig",
    "Flux3KleinImageSize",
    "Flux3KleinLoRAInput",
    "Flux3KleinTextToImageConfig",
    "Flux3KleinTextToImageLoraConfig",
    "Flux3TextToImageConfig",
    "Flux3TextToVideoConfig",
    "Flux3TextToVideoDraftConfig",
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
    "GptImage26FlareEditConfig",
    "GptImage26FlareTextToImageConfig",
    "GptImage26SunburstEditConfig",
    "GptImage26SunburstTextToImageConfig",
    "GrokImagineImageV20AspectRatio",
    "GrokImagineImageV20BaseConfig",
    "GrokImagineImageV20EditAspectRatio",
    "GrokImagineImageV20EditConfig",
    "GrokImagineImageV20TextToImageConfig",
    "GrokImagineVideoV15AspectRatio",
    "GrokImagineVideoV15ImageToVideoConfig",
    "GrokImagineVideoV15LiteImageToVideoConfig",
    "GrokImagineVideoV15LiteKeyframe",
    "GrokImagineVideoV15LiteTextToVideoConfig",
    "GrokImagineVideoV15ReferenceResolution",
    "GrokImagineVideoV15ReferenceToVideoConfig",
    "GrokImagineVideoV15Resolution",
    "GrokImagineVideoV15TextToVideoConfig",
    "H3LoraInput",
    "H3MaxCameraKeyframe",
    "H3MaxTurboReferenceCondition",
    "HappyHorseImageToVideoConfig",
    "HappyHorseReferenceToVideoConfig",
    "HappyHorseTextToVideoConfig",
    "HappyHorseVideoEditConfig",
    "HeygenVideoImageToVideoConfig",
    "HeygenVideoReferenceToVideoConfig",
    "HeygenVideoTextToVideoConfig",
    "Hyper3dLowpolyImageTo3dConfig",
    "Hyper3dLowpolyMeshTo3dConfig",
    "Hyper3dLowpolyTextTo3dConfig",
    "Hyper3dRigHierarchyNode",
    "Hyper3dRiggingAnimationsConfig",
    "Hyper3dRiggingConfig",
    "HeygenVoiceConfig",
    "IdeogramV4Config",
    "IdeogramV4FastConfig",
    "IdeogramV4ImageSize",
    "IdeogramV4ImageToImageConfig",
    "IdeogramV4ImageToImageLoraConfig",
    "IdeogramV4InstantConfig",
    "IdeogramV4LoraConfig",
    "IdeogramV4LoRAInput",
    "IdeogramV4TilingConfig",
    "IdeogramV4TilingLoraConfig",
    "IdeogramV46Config",
    "IdeogramV46ContextWindowBox",
    "IdeogramV46EditConfig",
    "IdeogramVectorImageToVectorConfig",
    "IdeogramVectorTextToVectorConfig",
    "IrisZDepthConfig",
    "IrisZDepthToImageConfig",
    "IrisZImageSize",
    "IrisZSmallDepthConfig",
    "IrisZSmallDepthToImageConfig",
    "IrisZSmallTextToImageConfig",
    "IrisZSmallTextToRgbdConfig",
    "IrisZTextToImageConfig",
    "IrisZTextToRgbdConfig",
    "ImageSize",
    "JobConfig",
    "Kandinsky6ProImageToVideoConfig",
    "Kandinsky6ProTextToVideoConfig",
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
    "KlingV4Element",
    "KlingV4FlashElement",
    "KlingV4Shot",
    "KlingV4FlashImageToVideoConfig",
    "KlingV4FlashReferenceToVideoConfig",
    "KlingV4FlashTextToVideoConfig",
    "KlingV4FlashVideoToVideoConfig",
    "KlingV4ImageElement",
    "KlingV4ImageToImageConfig",
    "KlingV4LongImageConfig",
    "KlingV4TextToImageConfig",
    "KlingV4ImageToVideoConfig",
    "KlingV4ReferenceToVideoConfig",
    "KlingV4TextToVideoConfig",
    "KlingV4VideoToVideoEditConfig",
    "KlingVideoO3StandardTextToVideoConfig",
    "KlingVideoO3StandardImageToVideoConfig",
    "KlingVideoO3StandardReferenceToVideoConfig",
    "KlingVideoO3StandardVideoToVideoEditConfig",
    "KlingVideoO3VideoToVideoReferenceConfig",
    "KlingVideoV3StandardTextToVideoConfig",
    "KlingVideoV3StandardImageToVideoConfig",
    "KlingVideoV3StandardMotionControlConfig",
    "KlingVideoV3TurboTextToVideoConfig",
    "KlingVideoV3TurboImageToVideoConfig",
    "Krea3EditConfig",
    "Krea3EditLoraConfig",
    "Krea3EditRegion",
    "Krea3ImageSize",
    "Krea3LoRAInput",
    "Krea3TextToImageConfig",
    "Krea3TextToImageLoraConfig",
    "Ltx25AlphaGenConfig",
    "Ltx25HdrConfig",
    "Ltx25ReframeAnchor",
    "Ltx25ReframeConfig",
    "Ltx25ReframeRectangle",
    "Ltx25UpscaleConfig",
    "KotobaSttV1SpeechToTextConfig",
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
    "MaiImage27EditConfig",
    "MaiImage27FlashEditConfig",
    "MaiImage27FlashTextToImageConfig",
    "MaiImage27ImageSize",
    "MaiImage27TextToImageConfig",
    "MarigoldV2Config",
    "MarigoldV2ImageSize",
    "MatrixAxes",
    "MatrixAxis",
    "MeshyN1RetextureConfig",
    "MeshyReliefConfig",
    "MeshyRiggingConfig",
    "MeshyRiggingMultiAnimationConfig",
    "MeshyT2ImageTo3dConfig",
    "MeshyT2TextTo3dConfig",
    "MeshyT25ImageTo3dConfig",
    "MeshyT25TextTo3dConfig",
    "MeshyV6LiteRetextureConfig",
    "MeshyV6RetextureConfig",
    "MeshyV7ImageTo3dConfig",
    "MeshyV7RetextureConfig",
    "MeshyV7TextTo3dConfig",
    "Moge2Config",
    "Moge3Config",
    "IdolConfig",
    "IdolMaxConfig",
    "H3ImageLoraInput",
    "MinimaxH3ImageEditConfig",
    "MinimaxH3ImageHighspeedEditConfig",
    "MinimaxH3ImageHighspeedTextToImageConfig",
    "MinimaxH3ImageSize",
    "MinimaxH3ImageTextToImageConfig",
    "MinimaxH3Max3dToVideoConfig",
    "MinimaxH3ImageToVideoConfig",
    "MinimaxH3ImageToVideoLoraConfig",
    "MinimaxH3MaxCameraControlsConfig",
    "MinimaxH3MaxExtendVideoConfig",
    "MinimaxH3MaxImageToVideoConfig",
    "MinimaxH3MaxInsertVideoConfig",
    "MinimaxH3MaxLipSyncImageToVideoConfig",
    "MinimaxH3MaxRecastConfig",
    "MinimaxH3MaxReferenceToVideoConfig",
    "MinimaxH3MaxReframeVideoConfig",
    "MinimaxH3MaxRelightConfig",
    "MinimaxH3MaxTextToVideoConfig",
    "MinimaxH3MaxTurboExtendVideoConfig",
    "MinimaxH3MaxTurboImageToVideoConfig",
    "MinimaxH3MaxTurboReferenceToVideoConfig",
    "MinimaxH3MaxTurboTextToVideoConfig",
    "MinimaxH3ReferenceToVideoConfig",
    "MinimaxH3ReferenceToVideoLoraConfig",
    "MinimaxH3TextToVideoConfig",
    "MinimaxH3TextToVideoLoraConfig",
    "MinimaxMusic3Config",
    "Mischief1ImageToVideoConfig",
    "MossImageConfig",
    "MossImageSize",
    "MurekaFilesUploadConfig",
    "MurekaInstrumentalConfig",
    "MurekaSongConfig",
    "MurekaSongExtendConfig",
    "MurekaSongRemixConfig",
    "MurekaSoundtrackConfig",
    "MurekaTrackConfig",
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
    "PixverseV6ExtendConfig",
    "PixverseV6MaxImageToVideoConfig",
    "PixverseV6MaxTextToVideoConfig",
    "PixverseV6TransitionConfig",
    "QwenAudio3TtsConfig",
    "QwenImage3EditConfig",
    "QwenImage3ImageSize",
    "QwenImage3TextToImageConfig",
    "RecraftV41FlashV2ImageSize",
    "RecraftV41FlashV2RGBColor",
    "RecraftV41FlashV2TextToImageConfig",
    "RecraftVectorizeProConfig",
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
    "SeedreamV5FlashEditConfig",
    "SeedreamV5FlashLayerizeConfig",
    "SeedreamV5FlashTextToImageConfig",
    "SeedreamV5LiteEditConfig",
    "SeedreamV5LiteImageSize",
    "SeedreamV5LiteTextToImageConfig",
    "SeedreamV5ProEditConfig",
    "SeedreamV5ProImageSize",
    "SeedreamV5ProLayerizeConfig",
    "SeedreamV5ProTextToImageConfig",
    "SeedreamV5ProUsEditConfig",
    "SeedreamV5ProUsTextToImageConfig",
    "SeedreamV55EditConfig",
    "SeedreamV55LayerizeConfig",
    "SeedreamV55TextToImageConfig",
    "SeedTtsV3Config",
    "Seedance2FastImageToVideoConfig",
    "Seedance2FastReferenceToVideoConfig",
    "Seedance2FastTextToVideoConfig",
    "Seedance2ImageToVideoConfig",
    "Seedance2MiniImageToVideoConfig",
    "Seedance2MiniReferenceToVideoConfig",
    "Seedance2MiniTextToVideoConfig",
    "Seedance2ReferenceToVideoConfig",
    "Seedance2TextToVideoConfig",
    "Seedance25FlashImageToVideoConfig",
    "Seedance25FlashReferenceToVideoConfig",
    "Seedance25FlashTextToVideoConfig",
    "Seedance2UsImageToVideoConfig",
    "Seedance2UsReferenceToVideoConfig",
    "Seedance2UsTextToVideoConfig",
    "Seedance25ImageToVideoConfig",
    "Seedance25ReferenceToVideoConfig",
    "Seedance25TextToVideoConfig",
    "Seedance25UsDraftCompleteConfig",
    "Seedance25UsImageToVideoConfig",
    "Seedance25UsReferenceToVideoConfig",
    "Seedance25UsTextToVideoConfig",
    "SoniloV11SfxSegment",
    "SoniloV11VideoToSoundEffectsConfig",
    "SoniloV11TextToMusicConfig",
    "SoniloV11TextToSoundEffectsConfig",
    "SoniloV11VideoToMusicConfig",
    "SoniloV11VideoToVideoMusicConfig",
    "SoniloV11VideoToVideoSoundEffectsConfig",
    "SUPPORTED_APP_IDS",
    "TopazAdjustImageConfig",
    "TopazDeblurVideoConfig",
    "TopazDenoiseImageConfig",
    "TopazDenoiseVideoConfig",
    "TopazInterpolateVideoConfig",
    "TopazRestoreImageConfig",
    "TopazSdrToHdrVideoConfig",
    "TopazSharpenImageConfig",
    "TopazUpscaleImageCreativeConfig",
    "TopazUpscaleImageGenerativeConfig",
    "TopazUpscaleImagePrecisionConfig",
    "TopazUpscaleImageTransparentConfig",
    "TopazUpscaleVideoCreativeConfig",
    "TopazUpscaleVideoGenerativeConfig",
    "TopazUpscaleVideoPrecisionConfig",
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
    "ViduQ3ImageToVideoTurboConfig",
    "ViduQ3ImageToVideoConfig",
    "ViduQ3ReferenceToVideoConfig",
    "ViduQ3ReferenceToVideoMixConfig",
    "ViduQ3TextToVideoTurboConfig",
    "ViduQ3TextToVideoConfig",
    "ViduQ4ImageToVideoConfig",
    "ViduQ4ReferenceToVideoConfig",
    "VirtualTryOnConfig",
    "Wan30ImageToVideoConfig",
    "Wan30PrimeImageToVideoConfig",
    "Wan30ReferenceToVideoConfig",
    "Wan30PrimeReferenceToVideoConfig",
    "Wan30TextToVideoConfig",
    "Wan30PrimeTextToVideoConfig",
    "config_class_for_app_id",
    "parameter_field_is_list",
    "validate_job_schema",
    "validate_parameters",
]
