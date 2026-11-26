from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import (
    GptImage2Config,
    GptImage2EditConfig,
    HappyHorseImageToVideoConfig,
    HappyHorseReferenceToVideoConfig,
    HappyHorseTextToVideoConfig,
    HappyHorseVideoEditConfig,
    KlingVideoO3ProImageToVideoConfig,
    KlingVideoO3ProReferenceToVideoConfig,
    KlingVideoO3ProTextToVideoConfig,
    KlingVideoO3ProVideoToVideoEditConfig,
    KlingVideoO34kImageToVideoConfig,
    KlingVideoO34kReferenceToVideoConfig,
    KlingVideoO34kTextToVideoConfig,
    KlingVideoV3ProImageToVideoConfig,
    KlingVideoV3ProMotionControlConfig,
    KlingVideoV3ProTextToVideoConfig,
    KlingVideoV34kImageToVideoConfig,
    KlingVideoV34kTextToVideoConfig,
    LumaRay32ImageToVideoConfig,
    LumaRay32ReframeConfig,
    LumaRay32TextToVideoConfig,
    LumaRay32VideoToVideoConfig,
    NanoBanana2Config,
    NanoBanana2EditConfig,
    Seedance2ImageToVideoConfig,
    Seedance2ReferenceToVideoConfig,
    Seedance2TextToVideoConfig,
    SeedreamV5LiteEditConfig,
    SeedreamV5LiteTextToImageConfig,
    SeedreamV45EditConfig,
    SeedreamV45TextToImageConfig,
    Veo31FirstLastFrameToVideoConfig,
    Veo31ImageToVideoConfig,
    Veo31ReferenceToVideoConfig,
    Veo31TextToVideoConfig,
    ViduQ3ImageToVideoConfig,
    ViduQ3ReferenceToVideoConfig,
    ViduQ3ReferenceToVideoMixConfig,
    ViduQ3TextToVideoConfig,
    validate_parameters,
)


def test_validate_parameters_warns_and_returns_none_for_unregistered_app_id() -> None:
    with pytest.warns(UserWarning, match="fal-ai/not-registered") as record:
        validated = validate_parameters("fal-ai/not-registered", {"prompt": "a cat"})

    assert validated is None
    assert len(record) == 1
    assert "fal-ai/not-registered" in str(record[0].message)


def test_validate_parameters_returns_registered_config_instance() -> None:
    validated = validate_parameters("fal-ai/nano-banana-2", {"prompt": "a cat on a mat"})

    assert isinstance(validated, NanoBanana2Config)


def test_validate_parameters_returns_registered_edit_config_instance() -> None:
    validated = validate_parameters(
        "fal-ai/nano-banana-2/edit",
        {"prompt": "make it warm", "image_urls": ["./input.png"]},
    )

    assert isinstance(validated, NanoBanana2EditConfig)


def test_validate_parameters_returns_registered_gpt_image_2_config_instance() -> None:
    validated = validate_parameters("openai/gpt-image-2", {"prompt": "a cat on a mat"})

    assert isinstance(validated, GptImage2Config)


def test_validate_parameters_returns_registered_gpt_image_2_edit_config_instance() -> None:
    validated = validate_parameters(
        "openai/gpt-image-2/edit",
        {"prompt": "make it warm", "image_urls": ["./input.png"]},
    )

    assert isinstance(validated, GptImage2EditConfig)


def test_validate_parameters_returns_registered_seedream_v45_text_to_image_config() -> None:
    validated = validate_parameters(
        "fal-ai/bytedance/seedream/v4.5/text-to-image",
        {"prompt": "A bright editorial product photo."},
    )

    assert isinstance(validated, SeedreamV45TextToImageConfig)


def test_validate_parameters_returns_registered_seedream_v45_edit_config() -> None:
    validated = validate_parameters(
        "fal-ai/bytedance/seedream/v4.5/edit",
        {
            "prompt": "Replace the product while keeping the setting.",
            "image_urls": ["https://example.com/input.png"],
        },
    )

    assert isinstance(validated, SeedreamV45EditConfig)


def test_validate_parameters_returns_registered_seedream_v5_lite_text_to_image_config() -> None:
    validated = validate_parameters(
        "fal-ai/bytedance/seedream/v5/lite/text-to-image",
        {"prompt": "A bright editorial product photo."},
    )

    assert isinstance(validated, SeedreamV5LiteTextToImageConfig)


def test_validate_parameters_returns_registered_seedream_v5_lite_edit_config() -> None:
    validated = validate_parameters(
        "fal-ai/bytedance/seedream/v5/lite/edit",
        {
            "prompt": "Replace the product while keeping the setting.",
            "image_urls": ["https://example.com/input.png"],
        },
    )

    assert isinstance(validated, SeedreamV5LiteEditConfig)


def test_validate_parameters_returns_registered_seedance2_image_to_video_config_instance() -> None:
    validated = validate_parameters(
        "bytedance/seedance-2.0/image-to-video",
        {
            "prompt": "The camera slowly pushes in on the city skyline.",
            "image_url": "https://example.com/start.png",
        },
    )

    assert isinstance(validated, Seedance2ImageToVideoConfig)


def test_validate_parameters_returns_registered_seedance2_text_to_video_config_instance() -> None:
    validated = validate_parameters(
        "bytedance/seedance-2.0/text-to-video",
        {
            "prompt": "The camera slowly pushes through a glass corridor at sunrise.",
        },
    )

    assert isinstance(validated, Seedance2TextToVideoConfig)


def test_validate_parameters_returns_registered_seedance2_reference_to_video_config() -> None:
    validated = validate_parameters(
        "bytedance/seedance-2.0/reference-to-video",
        {
            "prompt": "Animate @Image1 using @Video1 as a motion reference.",
            "image_urls": ["https://example.com/hero.png"],
            "video_urls": ["https://example.com/motion.mp4"],
        },
    )

    assert isinstance(validated, Seedance2ReferenceToVideoConfig)


def test_validate_parameters_returns_registered_kling_v3_motion_control_config_instance() -> None:
    validated = validate_parameters(
        "fal-ai/kling-video/v3/pro/motion-control",
        {
            "image_url": "https://example.com/character.png",
            "video_url": "https://example.com/motion.mp4",
            "character_orientation": "image",
        },
    )

    assert isinstance(validated, KlingVideoV3ProMotionControlConfig)


def test_validate_parameters_returns_registered_kling_v3_pro_image_to_video_config() -> None:
    validated = validate_parameters(
        "fal-ai/kling-video/v3/pro/image-to-video",
        {
            "prompt": "The subject slowly turns toward the camera.",
            "start_image_url": "https://example.com/start.png",
        },
    )

    assert isinstance(validated, KlingVideoV3ProImageToVideoConfig)


def test_validate_parameters_returns_registered_kling_v3_4k_image_to_video_config() -> None:
    validated = validate_parameters(
        "fal-ai/kling-video/v3/4k/image-to-video",
        {
            "prompt": "The subject slowly turns toward the camera.",
            "start_image_url": "https://example.com/start.png",
        },
    )

    assert isinstance(validated, KlingVideoV34kImageToVideoConfig)


def test_validate_parameters_returns_registered_kling_v3_pro_text_to_video_config() -> None:
    validated = validate_parameters(
        "fal-ai/kling-video/v3/pro/text-to-video",
        {"prompt": "A cinematic city street fills with morning light."},
    )

    assert isinstance(validated, KlingVideoV3ProTextToVideoConfig)


def test_validate_parameters_returns_registered_kling_v3_4k_text_to_video_config() -> None:
    validated = validate_parameters(
        "fal-ai/kling-video/v3/4k/text-to-video",
        {"prompt": "A cinematic city street fills with morning light."},
    )

    assert isinstance(validated, KlingVideoV34kTextToVideoConfig)


def test_validate_parameters_returns_registered_kling_o3_pro_text_to_video_config() -> None:
    validated = validate_parameters(
        "fal-ai/kling-video/o3/pro/text-to-video",
        {"prompt": "A cinematic city street fills with morning light."},
    )

    assert isinstance(validated, KlingVideoO3ProTextToVideoConfig)


def test_validate_parameters_returns_registered_kling_o3_4k_text_to_video_config() -> None:
    validated = validate_parameters(
        "fal-ai/kling-video/o3/4k/text-to-video",
        {"prompt": "A cinematic city street fills with morning light."},
    )

    assert isinstance(validated, KlingVideoO34kTextToVideoConfig)


def test_validate_parameters_returns_registered_kling_o3_pro_image_to_video_config() -> None:
    validated = validate_parameters(
        "fal-ai/kling-video/o3/pro/image-to-video",
        {
            "prompt": "The subject slowly turns toward the camera.",
            "image_url": "https://example.com/start.png",
        },
    )

    assert isinstance(validated, KlingVideoO3ProImageToVideoConfig)


def test_validate_parameters_returns_registered_kling_o3_4k_image_to_video_config() -> None:
    validated = validate_parameters(
        "fal-ai/kling-video/o3/4k/image-to-video",
        {
            "prompt": "The subject slowly turns toward the camera.",
            "image_url": "https://example.com/start.png",
        },
    )

    assert isinstance(validated, KlingVideoO34kImageToVideoConfig)


def test_validate_parameters_returns_registered_kling_o3_pro_reference_to_video_config() -> None:
    validated = validate_parameters(
        "fal-ai/kling-video/o3/pro/reference-to-video",
        {
            "prompt": "@Element1 enters the scene.",
            "elements": [{"frontal_image_url": "https://example.com/front.png"}],
        },
    )

    assert isinstance(validated, KlingVideoO3ProReferenceToVideoConfig)


def test_validate_parameters_returns_registered_kling_o3_4k_reference_to_video_config() -> None:
    validated = validate_parameters(
        "fal-ai/kling-video/o3/4k/reference-to-video",
        {
            "prompt": "@Image1 sets the style.",
            "image_urls": ["https://example.com/style.png"],
        },
    )

    assert isinstance(validated, KlingVideoO34kReferenceToVideoConfig)


def test_validate_parameters_returns_registered_kling_o3_pro_video_to_video_edit_config() -> None:
    validated = validate_parameters(
        "fal-ai/kling-video/o3/pro/video-to-video/edit",
        {
            "prompt": "Replace the background with snow.",
            "video_url": "https://example.com/source.mp4",
        },
    )

    assert isinstance(validated, KlingVideoO3ProVideoToVideoEditConfig)


def test_validate_parameters_returns_registered_happy_horse_text_to_video_config() -> None:
    validated = validate_parameters(
        "alibaba/happy-horse/text-to-video",
        {"prompt": "A cinematic city street fills with morning light."},
    )

    assert isinstance(validated, HappyHorseTextToVideoConfig)


def test_validate_parameters_returns_registered_happy_horse_image_to_video_config() -> None:
    validated = validate_parameters(
        "alibaba/happy-horse/image-to-video",
        {"image_url": "https://example.com/start.png"},
    )

    assert isinstance(validated, HappyHorseImageToVideoConfig)


def test_validate_parameters_returns_registered_happy_horse_reference_to_video_config() -> None:
    validated = validate_parameters(
        "alibaba/happy-horse/reference-to-video",
        {
            "prompt": "Animate character1.",
            "image_urls": ["https://example.com/character.png"],
        },
    )

    assert isinstance(validated, HappyHorseReferenceToVideoConfig)


def test_validate_parameters_returns_registered_happy_horse_video_edit_config() -> None:
    validated = validate_parameters(
        "alibaba/happy-horse/video-edit",
        {
            "video_url": "https://example.com/source.mp4",
            "prompt": "Recolor the sky to a deep purple sunset.",
        },
    )

    assert isinstance(validated, HappyHorseVideoEditConfig)


def test_validate_parameters_returns_registered_luma_ray_3_2_text_to_video_config() -> None:
    validated = validate_parameters(
        "luma/agent/ray/v3.2/text-to-video",
        {"prompt": "A cinematic city street fills with morning light."},
    )

    assert isinstance(validated, LumaRay32TextToVideoConfig)


def test_validate_parameters_returns_registered_luma_ray_3_2_image_to_video_config() -> None:
    validated = validate_parameters(
        "luma/agent/ray/v3.2/image-to-video",
        {
            "prompt": "The subject slowly turns toward the camera.",
            "image_url": "https://example.com/start.png",
        },
    )

    assert isinstance(validated, LumaRay32ImageToVideoConfig)


def test_validate_parameters_returns_registered_luma_ray_3_2_video_to_video_config() -> None:
    validated = validate_parameters(
        "luma/agent/ray/v3.2/video-to-video",
        {
            "prompt": "Replace the background with snow.",
            "video_url": "https://example.com/source.mp4",
        },
    )

    assert isinstance(validated, LumaRay32VideoToVideoConfig)


def test_validate_parameters_returns_registered_luma_ray_3_2_reframe_config() -> None:
    validated = validate_parameters(
        "luma/agent/ray/v3.2/reframe",
        {
            "prompt": "Extend the scene into widescreen.",
            "video_url": "https://example.com/source.mp4",
            "aspect_ratio": "21:9",
        },
    )

    assert isinstance(validated, LumaRay32ReframeConfig)


def test_validate_parameters_returns_registered_veo3_1_text_to_video_config() -> None:
    validated = validate_parameters(
        "fal-ai/veo3.1",
        {"prompt": "A cinematic city street fills with morning light."},
    )

    assert isinstance(validated, Veo31TextToVideoConfig)


def test_validate_parameters_returns_registered_veo3_1_image_to_video_config() -> None:
    validated = validate_parameters(
        "fal-ai/veo3.1/image-to-video",
        {
            "prompt": "The subject slowly turns toward the camera.",
            "image_url": "https://example.com/start.png",
        },
    )

    assert isinstance(validated, Veo31ImageToVideoConfig)


def test_validate_parameters_returns_registered_veo3_1_first_last_frame_to_video_config() -> None:
    validated = validate_parameters(
        "fal-ai/veo3.1/first-last-frame-to-video",
        {
            "prompt": "Animate between the first and last frames.",
            "first_frame_url": "https://example.com/first.png",
            "last_frame_url": "https://example.com/last.png",
        },
    )

    assert isinstance(validated, Veo31FirstLastFrameToVideoConfig)


def test_validate_parameters_returns_registered_veo3_1_reference_to_video_config() -> None:
    validated = validate_parameters(
        "fal-ai/veo3.1/reference-to-video",
        {
            "prompt": "Animate the reference images.",
            "image_urls": ["https://example.com/ref.png"],
        },
    )

    assert isinstance(validated, Veo31ReferenceToVideoConfig)


def test_validate_parameters_returns_registered_vidu_q3_text_to_video_config() -> None:
    validated = validate_parameters(
        "fal-ai/vidu/q3/text-to-video",
        {"prompt": "A cinematic city street fills with morning light."},
    )

    assert isinstance(validated, ViduQ3TextToVideoConfig)


def test_validate_parameters_returns_registered_vidu_q3_image_to_video_config() -> None:
    validated = validate_parameters(
        "fal-ai/vidu/q3/image-to-video",
        {"image_url": "https://example.com/start.png"},
    )

    assert isinstance(validated, ViduQ3ImageToVideoConfig)


def test_validate_parameters_returns_registered_vidu_q3_reference_to_video_config() -> None:
    validated = validate_parameters(
        "fal-ai/vidu/q3/reference-to-video",
        {
            "prompt": "Animate the reference images.",
            "reference_image_urls": ["https://example.com/ref.png"],
        },
    )

    assert isinstance(validated, ViduQ3ReferenceToVideoConfig)


def test_validate_parameters_returns_registered_vidu_q3_reference_to_video_mix_config() -> None:
    validated = validate_parameters(
        "fal-ai/vidu/q3/reference-to-video/mix",
        {
            "prompt": "Animate the reference images.",
            "reference_image_urls": ["https://example.com/ref.png"],
        },
    )

    assert isinstance(validated, ViduQ3ReferenceToVideoMixConfig)


def test_validate_parameters_propagates_validation_error_for_registered_app_id() -> None:
    with pytest.raises(ValidationError):
        validate_parameters("fal-ai/nano-banana-2", {"prompt": "no", "num_images": 5})


def test_validate_parameters_does_not_depend_on_fal_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("FAL_KEY", raising=False)

    validated = validate_parameters("fal-ai/nano-banana-2", {"prompt": "a cat on a mat"})

    assert isinstance(validated, NanoBanana2Config)
