from __future__ import annotations

from pydantic import TypeAdapter

from falx.models import (
    SUPPORTED_APP_IDS,
    FalConfig,
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
    Sam31ImageConfig,
    Sam31ImageRleConfig,
    Sam31VideoConfig,
    Sam31VideoRleConfig,
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
    config_class_for_app_id,
)


def test_supported_app_ids_lists_initial_registered_models() -> None:
    assert len(SUPPORTED_APP_IDS) == 273
    assert "fal-ai/gemini-tts" in SUPPORTED_APP_IDS
    assert "fal-ai/gemini-3.1-flash-tts" in SUPPORTED_APP_IDS
    assert "google/gemini-3.8-flash-tts" in SUPPORTED_APP_IDS
    assert "google/gemini-3.8-flash-lite-tts" in SUPPORTED_APP_IDS
    assert "fal-ai/lyria2" in SUPPORTED_APP_IDS
    assert "fal-ai/lyria3" in SUPPORTED_APP_IDS
    assert "fal-ai/lyria3/pro" in SUPPORTED_APP_IDS
    assert "google/lyria-3.5" in SUPPORTED_APP_IDS
    assert "google/virtual-try-on" in SUPPORTED_APP_IDS
    assert "blackforestlabs/flux-3/edit-video" in SUPPORTED_APP_IDS
    assert "bria/increase-resolution" in SUPPORTED_APP_IDS
    assert "bria/video/background-removal" in SUPPORTED_APP_IDS
    assert "bria/video/background-removal/v3" in SUPPORTED_APP_IDS
    assert "bria/video/background-removal/green-screen-despill" in SUPPORTED_APP_IDS
    assert "bria/video/erase/keypoints" in SUPPORTED_APP_IDS
    assert "bria/video/erase/mask" in SUPPORTED_APP_IDS
    assert "bria/video/erase/prompt" in SUPPORTED_APP_IDS
    assert "bria/video/increase-resolution" in SUPPORTED_APP_IDS
    assert "fal-ai/sam-3-1/image" in SUPPORTED_APP_IDS
    assert "fal-ai/sam-3-1/image-rle" in SUPPORTED_APP_IDS
    assert "fal-ai/sam-3-1/video" in SUPPORTED_APP_IDS
    assert "fal-ai/sam-3-1/video-rle" in SUPPORTED_APP_IDS
    assert "openai/gpt-image-2" in SUPPORTED_APP_IDS
    assert "openai/gpt-image-2/edit" in SUPPORTED_APP_IDS
    assert "openai/gpt-image-2.5/flare/text-to-image" in SUPPORTED_APP_IDS
    assert "openai/gpt-image-2.5/flare/edit" in SUPPORTED_APP_IDS
    assert "openai/gpt-image-2.5/sunburst/text-to-image" in SUPPORTED_APP_IDS
    assert "openai/gpt-image-2.5/sunburst/edit" in SUPPORTED_APP_IDS
    assert "fal-ai/nano-banana-2" in SUPPORTED_APP_IDS
    assert "fal-ai/nano-banana-2/edit" in SUPPORTED_APP_IDS
    assert "fal-ai/nano-banana" in SUPPORTED_APP_IDS
    assert "fal-ai/nano-banana/edit" in SUPPORTED_APP_IDS
    assert "fal-ai/gemini-25-flash-image" in SUPPORTED_APP_IDS
    assert "fal-ai/gemini-25-flash-image/edit" in SUPPORTED_APP_IDS
    assert "fal-ai/nano-banana-pro" in SUPPORTED_APP_IDS
    assert "fal-ai/nano-banana-pro/edit" in SUPPORTED_APP_IDS
    assert "fal-ai/gemini-3-pro-image-preview" in SUPPORTED_APP_IDS
    assert "fal-ai/gemini-3-pro-image-preview/edit" in SUPPORTED_APP_IDS
    assert "fal-ai/gemini-3.1-flash-image-preview" in SUPPORTED_APP_IDS
    assert "fal-ai/gemini-3.1-flash-image-preview/edit" in SUPPORTED_APP_IDS
    assert "google/nano-banana-lite" in SUPPORTED_APP_IDS
    assert "google/nano-banana-lite/edit" in SUPPORTED_APP_IDS
    assert "fal-ai/bytedance/seedream/v4.5/text-to-image" in SUPPORTED_APP_IDS
    assert "fal-ai/bytedance/seedream/v4.5/edit" in SUPPORTED_APP_IDS
    assert "fal-ai/bytedance/seedream/v5/lite/text-to-image" in SUPPORTED_APP_IDS
    assert "fal-ai/bytedance/seedream/v5/lite/edit" in SUPPORTED_APP_IDS
    assert "bytedance/seedream/v5/flash/text-to-image" in SUPPORTED_APP_IDS
    assert "bytedance/seedream/v5/flash/edit" in SUPPORTED_APP_IDS
    assert "bytedance/seedream/v5/flash/layerize" in SUPPORTED_APP_IDS
    assert "bytedance/seedream/v5/lite/text-to-image" in SUPPORTED_APP_IDS
    assert "bytedance/seedream/v5/lite/edit" in SUPPORTED_APP_IDS
    assert "bytedance/seedream/v5/pro/us/text-to-image" in SUPPORTED_APP_IDS
    assert "bytedance/seedream/v5/pro/us/edit" in SUPPORTED_APP_IDS
    assert "bytedance/seedance-2.0/image-to-video" in SUPPORTED_APP_IDS
    assert "bytedance/seedance-2.0/reference-to-video" in SUPPORTED_APP_IDS
    assert "bytedance/seedance-2.0/text-to-video" in SUPPORTED_APP_IDS
    assert "bytedance/seedance-2.0/fast/image-to-video" in SUPPORTED_APP_IDS
    assert "bytedance/seedance-2.0/fast/reference-to-video" in SUPPORTED_APP_IDS
    assert "bytedance/seedance-2.0/fast/text-to-video" in SUPPORTED_APP_IDS
    assert "bytedance/seedance-2.0/mini/image-to-video" in SUPPORTED_APP_IDS
    assert "bytedance/seedance-2.0/mini/reference-to-video" in SUPPORTED_APP_IDS
    assert "bytedance/seedance-2.0/mini/text-to-video" in SUPPORTED_APP_IDS
    assert "bytedance/seedance-2.5/flash/image-to-video" in SUPPORTED_APP_IDS
    assert "bytedance/seedance-2.5/flash/reference-to-video" in SUPPORTED_APP_IDS
    assert "bytedance/seedance-2.5/flash/text-to-video" in SUPPORTED_APP_IDS
    assert "fal-ai/kling-video/v3/pro/image-to-video" in SUPPORTED_APP_IDS
    assert "fal-ai/kling-video/v3/4k/image-to-video" in SUPPORTED_APP_IDS
    assert "fal-ai/kling-video/v3/pro/text-to-video" in SUPPORTED_APP_IDS
    assert "fal-ai/kling-video/v3/4k/text-to-video" in SUPPORTED_APP_IDS
    assert "fal-ai/kling-video/v3/pro/motion-control" in SUPPORTED_APP_IDS
    assert "fal-ai/kling-video/o3/pro/text-to-video" in SUPPORTED_APP_IDS
    assert "fal-ai/kling-video/o3/pro/image-to-video" in SUPPORTED_APP_IDS
    assert "fal-ai/kling-video/o3/pro/reference-to-video" in SUPPORTED_APP_IDS
    assert "fal-ai/kling-video/o3/pro/video-to-video/edit" in SUPPORTED_APP_IDS
    assert "fal-ai/kling-video/o3/4k/text-to-video" in SUPPORTED_APP_IDS
    assert "fal-ai/kling-video/o3/4k/image-to-video" in SUPPORTED_APP_IDS
    assert "fal-ai/kling-video/o3/4k/reference-to-video" in SUPPORTED_APP_IDS
    assert "fal-ai/kling-video/o3/4k/video-to-video/edit" in SUPPORTED_APP_IDS
    assert "fal-ai/kling-video/o3/4k/video-to-video/reference" in SUPPORTED_APP_IDS
    assert "kling/v4/flash/image-to-video" in SUPPORTED_APP_IDS
    assert "kling/v4/flash/reference-to-video" in SUPPORTED_APP_IDS
    assert "kling/v4/flash/text-to-video" in SUPPORTED_APP_IDS
    assert "kling/v4/flash/video-to-video" in SUPPORTED_APP_IDS
    assert "kling/v4/image-to-image" in SUPPORTED_APP_IDS
    assert "kling/v4/long-image" in SUPPORTED_APP_IDS
    assert "kling/v4/text-to-image" in SUPPORTED_APP_IDS
    assert "kling/v4/image-to-video" in SUPPORTED_APP_IDS
    assert "kling/v4/reference-to-video" in SUPPORTED_APP_IDS
    assert "kling/v4/text-to-video" in SUPPORTED_APP_IDS
    assert "kling/v4/video-to-video/edit" in SUPPORTED_APP_IDS
    assert "alibaba/happy-horse/text-to-video" in SUPPORTED_APP_IDS
    assert "alibaba/happy-horse/image-to-video" in SUPPORTED_APP_IDS
    assert "alibaba/happy-horse/reference-to-video" in SUPPORTED_APP_IDS
    assert "alibaba/happy-horse/video-edit" in SUPPORTED_APP_IDS
    assert "fal-ai/veo3" in SUPPORTED_APP_IDS
    assert "fal-ai/veo3/fast" in SUPPORTED_APP_IDS
    assert "fal-ai/veo3/image-to-video" in SUPPORTED_APP_IDS
    assert "fal-ai/veo3/fast/image-to-video" in SUPPORTED_APP_IDS
    assert "fal-ai/veo3.1" in SUPPORTED_APP_IDS
    assert "fal-ai/veo3.1/image-to-video" in SUPPORTED_APP_IDS
    assert "fal-ai/veo3.1/first-last-frame-to-video" in SUPPORTED_APP_IDS
    assert "fal-ai/veo3.1/reference-to-video" in SUPPORTED_APP_IDS
    assert "fal-ai/veo3.1/extend-video" in SUPPORTED_APP_IDS
    assert "fal-ai/veo3.1/fast" in SUPPORTED_APP_IDS
    assert "fal-ai/veo3.1/fast/image-to-video" in SUPPORTED_APP_IDS
    assert "fal-ai/veo3.1/fast/first-last-frame-to-video" in SUPPORTED_APP_IDS
    assert "fal-ai/veo3.1/fast/reference-to-video" in SUPPORTED_APP_IDS
    assert "fal-ai/veo3.1/fast/extend-video" in SUPPORTED_APP_IDS
    assert "fal-ai/veo3.1/lite" in SUPPORTED_APP_IDS
    assert "fal-ai/veo3.1/lite/image-to-video" in SUPPORTED_APP_IDS
    assert "fal-ai/veo3.1/lite/first-last-frame-to-video" in SUPPORTED_APP_IDS
    assert "fal-ai/vidu/q3/text-to-video" in SUPPORTED_APP_IDS
    assert "fal-ai/vidu/q3/image-to-video" in SUPPORTED_APP_IDS
    assert "fal-ai/vidu/q3/reference-to-video" in SUPPORTED_APP_IDS
    assert "fal-ai/vidu/q3/reference-to-video/mix" in SUPPORTED_APP_IDS
    assert "luma/agent/ray/v3.2/text-to-video" in SUPPORTED_APP_IDS
    assert "luma/agent/ray/v3.2/image-to-video" in SUPPORTED_APP_IDS
    assert "luma/agent/ray/v3.2/video-to-video" in SUPPORTED_APP_IDS
    assert "luma/agent/ray/v3.2/reframe" in SUPPORTED_APP_IDS
    assert "minimax/h3-max-turbo/image-to-video" in SUPPORTED_APP_IDS
    assert "minimax/h3-max-turbo/reference-to-video" in SUPPORTED_APP_IDS
    assert "minimax/h3/image-to-video" in SUPPORTED_APP_IDS
    assert "minimax/h3/image-to-video/lora" in SUPPORTED_APP_IDS
    assert "minimax/h3/reference-to-video" in SUPPORTED_APP_IDS
    assert "minimax/h3/reference-to-video/lora" in SUPPORTED_APP_IDS
    assert "minimax/h3/text-to-video" in SUPPORTED_APP_IDS
    assert "minimax/h3/text-to-video/lora" in SUPPORTED_APP_IDS
    assert "minimax/h3-max-turbo/text-to-video" in SUPPORTED_APP_IDS
    assert "minimax/h3-max/reference-to-video" in SUPPORTED_APP_IDS
    assert "minimax/h3-max/camera-controls" in SUPPORTED_APP_IDS
    assert "minimax/h3-max/extend-video" in SUPPORTED_APP_IDS
    assert "minimax/h3-max-turbo/extend-video" in SUPPORTED_APP_IDS
    assert "minimax/h3-max/insert-video" in SUPPORTED_APP_IDS
    assert "minimax/h3-max/recast" in SUPPORTED_APP_IDS
    assert "minimax/h3-max/relight" in SUPPORTED_APP_IDS
    assert "minimax/h3-max/reframe-video" in SUPPORTED_APP_IDS
    assert "minimax/h3-max/3d-to-video" in SUPPORTED_APP_IDS
    assert "minimax/h3-max/lip-sync/image-to-video" in SUPPORTED_APP_IDS
    assert "meta/muse-image/edit" in SUPPORTED_APP_IDS
    assert "meta/muse-image/text-to-image" in SUPPORTED_APP_IDS
    assert "xai/grok-imagine-image/v2.0/edit" in SUPPORTED_APP_IDS
    assert "xai/grok-imagine-image/v2.0/text-to-image" in SUPPORTED_APP_IDS
    assert "xai/grok-imagine-video/v1.5/image-to-video" in SUPPORTED_APP_IDS
    assert "xai/grok-imagine-video/v1.5/reference-to-video" in SUPPORTED_APP_IDS
    assert "xai/grok-imagine-video/v1.5/text-to-video" in SUPPORTED_APP_IDS
    assert "google/gemini-omni-flash" in SUPPORTED_APP_IDS
    assert "google/gemini-omni-flash/edit" in SUPPORTED_APP_IDS
    assert "google/gemini-omni-flash/image-to-video" in SUPPORTED_APP_IDS
    assert "google/gemini-omni-flash/reference-to-video" in SUPPORTED_APP_IDS
    assert "google/gemini-omni-flash/v1.2/text-to-video" in SUPPORTED_APP_IDS
    assert "google/gemini-omni-flash/v1.2/image-to-video" in SUPPORTED_APP_IDS
    assert "google/gemini-omni-flash/v1.2/reference-to-video" in SUPPORTED_APP_IDS
    assert "google/gemini-omni-flash/v1.2/edit" in SUPPORTED_APP_IDS
    assert "google/gemini-omni-flash/v1.2/extend" in SUPPORTED_APP_IDS
    assert "google/gemini-omni-flash/v1.2/upscale" in SUPPORTED_APP_IDS


def test_registered_models_declare_random_seed_metadata() -> None:
    seeded_app_ids = {
        "blackforestlabs/flux-3-max/text-to-video",
        "blackforestlabs/flux-3-max/image-to-video",
        "blackforestlabs/flux-3-max/keyframes-to-video",
        "heygen/heygen-video/text-to-video",
        "heygen/heygen-video/image-to-video",
        "heygen/heygen-video/reference-to-video",
        "tbc/mischief-1/image-to-video",
        "fal-ai/vidu/q3/text-to-video/turbo",
        "fal-ai/vidu/q3/image-to-video/turbo",
        "alibaba/wan-3.0/text-to-video",
        "alibaba/wan-3.0/image-to-video",
        "alibaba/wan-3.0/reference-to-video",
        "blackforestlabs/flux-3/klein/text-to-image",
        "blackforestlabs/flux-3/klein/edit-image",
        "blackforestlabs/flux-3/klein/text-to-image/lora",
        "blackforestlabs/flux-3/klein/edit-image/lora",
        "blackforestlabs/flux-3/klein/base/text-to-image/lora",
        "blackforestlabs/flux-3/klein/base/edit-image/lora",
        "fal-ai/lyria2",
        "alibaba/qwen-image-3/edit",
        "alibaba/qwen-image-3/text-to-image",
        "ideogram/v4",
        "ideogram/v4/fast",
        "ideogram/v4/instant",
        "ideogram/v4/lora",
        "ideogram/v4/image-to-image",
        "ideogram/v4/image-to-image/lora",
        "ideogram/v4/tiling",
        "ideogram/v4/tiling/lora",
        "meshy/v7/text-to-3d",
        "minimax/music-3",
        "alibaba/happy-horse/image-to-video",
        "alibaba/happy-horse/reference-to-video",
        "alibaba/happy-horse/text-to-video",
        "alibaba/happy-horse/video-edit",
        "alibaba/wan-3.0-prime/image-to-video",
        "alibaba/wan-3.0-prime/reference-to-video",
        "alibaba/wan-3.0-prime/text-to-video",
        "bytedance/seedance-2.5/reference-to-video",
        "bytedance/seedance-2.5/flash/reference-to-video",
        "bytedance/seedance-2.5/us/reference-to-video",
        "fal-ai/bytedance/seedream/v4.5/edit",
        "fal-ai/bytedance/seedream/v4.5/text-to-image",
        "fal-ai/nano-banana-2",
        "fal-ai/nano-banana-2/edit",
        "google/nano-banana-2.1",
        "google/nano-banana-2.1/edit",
        "fal-ai/veo3",
        "fal-ai/veo3/fast",
        "fal-ai/veo3/image-to-video",
        "fal-ai/veo3/fast/image-to-video",
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
        "fal-ai/veo3.1",
        "fal-ai/veo3.1/image-to-video",
        "fal-ai/veo3.1/first-last-frame-to-video",
        "fal-ai/veo3.1/extend-video",
        "fal-ai/veo3.1/fast",
        "fal-ai/veo3.1/fast/image-to-video",
        "fal-ai/veo3.1/fast/first-last-frame-to-video",
        "fal-ai/veo3.1/fast/extend-video",
        "fal-ai/veo3.1/lite",
        "fal-ai/veo3.1/lite/image-to-video",
        "fal-ai/veo3.1/lite/first-last-frame-to-video",
        "fal-ai/vidu/q3/text-to-video",
        "fal-ai/vidu/q3/image-to-video",
        "fal-ai/vidu/q3/reference-to-video",
        "fal-ai/vidu/q3/reference-to-video/mix",
        "minimax/h3/image-to-video",
        "minimax/h3/image-to-video/lora",
        "minimax/h3/reference-to-video",
        "minimax/h3/reference-to-video/lora",
        "minimax/h3/text-to-video",
        "minimax/h3/text-to-video/lora",
        "fal-ai/vidu/q4/image-to-video",
        "fal-ai/vidu/q4/reference-to-video",
        "pixverse/v6/max/text-to-video",
        "pixverse/v6/max/image-to-video",
        "fal-ai/pixverse/v6/text-to-video",
        "fal-ai/pixverse/v6/image-to-video",
        "fal-ai/pixverse/v6/extend",
        "fal-ai/pixverse/v6/transition",
        "fal-ai/kandinsky6-pro/text-to-video",
        "fal-ai/kandinsky6-pro/image-to-video",
        "minimax/h3-max/camera-controls",
        "minimax/h3-max/extend-video",
        "minimax/h3-max-turbo/extend-video",
        "minimax/h3-max/insert-video",
        "minimax/h3-max/recast",
        "minimax/h3-max/relight",
        "minimax/h3-max/reframe-video",
        "minimax/h3-max/lip-sync/image-to-video",
        "minimax/h3-max/image-to-video",
        "minimax/h3-max/reference-to-video",
        "minimax/h3-max/text-to-video",
        "minimax/h3-max-turbo/image-to-video",
        "minimax/h3-max-turbo/reference-to-video",
        "minimax/h3-max-turbo/text-to-video",
    }

    metadata = {}
    for app_id in SUPPORTED_APP_IDS:
        config_class = config_class_for_app_id(app_id)
        assert config_class is not None
        metadata[app_id] = config_class.random_seed_field

    assert {app_id for app_id, field in metadata.items() if field == "seed"} == seeded_app_ids
    assert {app_id for app_id, field in metadata.items() if field is None} == (
        SUPPORTED_APP_IDS - seeded_app_ids
    )


def test_fal_config_discriminator_routes_to_nano_banana_2_config() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)

    parsed = adapter.validate_python({"app_id": "fal-ai/nano-banana-2", "prompt": "a cat on a mat"})

    assert isinstance(parsed, NanoBanana2Config)


def test_fal_config_discriminator_routes_to_nano_banana_2_edit_config() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)

    parsed = adapter.validate_python(
        {
            "app_id": "fal-ai/nano-banana-2/edit",
            "prompt": "make it cinematic",
            "image_urls": ["./local.png"],
        }
    )

    assert isinstance(parsed, NanoBanana2EditConfig)


def test_fal_config_discriminator_routes_to_gpt_image_2_config() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)

    parsed = adapter.validate_python({"app_id": "openai/gpt-image-2", "prompt": "a cat on a mat"})

    assert isinstance(parsed, GptImage2Config)


def test_fal_config_discriminator_routes_to_gpt_image_2_edit_config() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)

    parsed = adapter.validate_python(
        {
            "app_id": "openai/gpt-image-2/edit",
            "prompt": "make it cinematic",
            "image_urls": ["./local.png"],
        }
    )

    assert isinstance(parsed, GptImage2EditConfig)


def test_fal_config_discriminator_routes_to_seedream_v45_text_to_image_config() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)

    parsed = adapter.validate_python(
        {
            "app_id": "fal-ai/bytedance/seedream/v4.5/text-to-image",
            "prompt": "A bright editorial product photo.",
        }
    )

    assert isinstance(parsed, SeedreamV45TextToImageConfig)


def test_fal_config_discriminator_routes_to_seedream_v45_edit_config() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)

    parsed = adapter.validate_python(
        {
            "app_id": "fal-ai/bytedance/seedream/v4.5/edit",
            "prompt": "Replace the product while keeping the setting.",
            "image_urls": ["https://example.com/input.png"],
        }
    )

    assert isinstance(parsed, SeedreamV45EditConfig)


def test_fal_config_discriminator_routes_to_seedream_v5_lite_text_to_image_config() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)

    parsed = adapter.validate_python(
        {
            "app_id": "fal-ai/bytedance/seedream/v5/lite/text-to-image",
            "prompt": "A bright editorial product photo.",
        }
    )

    assert isinstance(parsed, SeedreamV5LiteTextToImageConfig)


def test_fal_config_discriminator_routes_to_seedream_v5_lite_edit_config() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)

    parsed = adapter.validate_python(
        {
            "app_id": "fal-ai/bytedance/seedream/v5/lite/edit",
            "prompt": "Replace the product while keeping the setting.",
            "image_urls": ["https://example.com/input.png"],
        }
    )

    assert isinstance(parsed, SeedreamV5LiteEditConfig)


def test_fal_config_discriminator_routes_to_seedance2_image_to_video_config() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)

    parsed = adapter.validate_python(
        {
            "app_id": "bytedance/seedance-2.0/image-to-video",
            "prompt": "The cat slowly turns its head and blinks.",
            "image_url": "https://example.com/cat.jpg",
        }
    )

    assert isinstance(parsed, Seedance2ImageToVideoConfig)


def test_fal_config_discriminator_routes_to_seedance2_text_to_video_config() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)

    parsed = adapter.validate_python(
        {
            "app_id": "bytedance/seedance-2.0/text-to-video",
            "prompt": "The camera slowly moves through a luminous city at dawn.",
        }
    )

    assert isinstance(parsed, Seedance2TextToVideoConfig)


def test_fal_config_discriminator_routes_to_seedance2_reference_to_video_config() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)

    parsed = adapter.validate_python(
        {
            "app_id": "bytedance/seedance-2.0/reference-to-video",
            "prompt": "Animate @Image1 with motion inspired by @Video1.",
            "image_urls": ["https://example.com/hero.png"],
            "video_urls": ["https://example.com/motion.mp4"],
        }
    )

    assert isinstance(parsed, Seedance2ReferenceToVideoConfig)


def test_fal_config_discriminator_routes_to_kling_v3_motion_control_config() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)

    parsed = adapter.validate_python(
        {
            "app_id": "fal-ai/kling-video/v3/pro/motion-control",
            "image_url": "https://example.com/character.jpg",
            "video_url": "https://example.com/motion.mp4",
            "character_orientation": "image",
        }
    )

    assert isinstance(parsed, KlingVideoV3ProMotionControlConfig)


def test_fal_config_discriminator_routes_to_kling_v3_pro_image_to_video_config() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)

    parsed = adapter.validate_python(
        {
            "app_id": "fal-ai/kling-video/v3/pro/image-to-video",
            "prompt": "The subject slowly turns toward the camera.",
            "start_image_url": "https://example.com/start.png",
        }
    )

    assert isinstance(parsed, KlingVideoV3ProImageToVideoConfig)


def test_fal_config_discriminator_routes_to_kling_v3_4k_image_to_video_config() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)

    parsed = adapter.validate_python(
        {
            "app_id": "fal-ai/kling-video/v3/4k/image-to-video",
            "prompt": "The subject slowly turns toward the camera.",
            "start_image_url": "https://example.com/start.png",
        }
    )

    assert isinstance(parsed, KlingVideoV34kImageToVideoConfig)


def test_fal_config_discriminator_routes_to_kling_v3_pro_text_to_video_config() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)

    parsed = adapter.validate_python(
        {
            "app_id": "fal-ai/kling-video/v3/pro/text-to-video",
            "prompt": "A cinematic city street fills with morning light.",
        }
    )

    assert isinstance(parsed, KlingVideoV3ProTextToVideoConfig)


def test_fal_config_discriminator_routes_to_kling_v3_4k_text_to_video_config() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)

    parsed = adapter.validate_python(
        {
            "app_id": "fal-ai/kling-video/v3/4k/text-to-video",
            "prompt": "A cinematic city street fills with morning light.",
        }
    )

    assert isinstance(parsed, KlingVideoV34kTextToVideoConfig)


def test_fal_config_discriminator_routes_to_kling_o3_pro_text_to_video_config() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)

    parsed = adapter.validate_python(
        {
            "app_id": "fal-ai/kling-video/o3/pro/text-to-video",
            "prompt": "A cinematic city street fills with morning light.",
        }
    )

    assert isinstance(parsed, KlingVideoO3ProTextToVideoConfig)


def test_fal_config_discriminator_routes_to_kling_o3_4k_text_to_video_config() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)

    parsed = adapter.validate_python(
        {
            "app_id": "fal-ai/kling-video/o3/4k/text-to-video",
            "prompt": "A cinematic city street fills with morning light.",
        }
    )

    assert isinstance(parsed, KlingVideoO34kTextToVideoConfig)


def test_fal_config_discriminator_routes_to_kling_o3_pro_image_to_video_config() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)

    parsed = adapter.validate_python(
        {
            "app_id": "fal-ai/kling-video/o3/pro/image-to-video",
            "prompt": "The subject slowly turns toward the camera.",
            "image_url": "https://example.com/start.png",
        }
    )

    assert isinstance(parsed, KlingVideoO3ProImageToVideoConfig)


def test_fal_config_discriminator_routes_to_kling_o3_4k_image_to_video_config() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)

    parsed = adapter.validate_python(
        {
            "app_id": "fal-ai/kling-video/o3/4k/image-to-video",
            "prompt": "The subject slowly turns toward the camera.",
            "image_url": "https://example.com/start.png",
        }
    )

    assert isinstance(parsed, KlingVideoO34kImageToVideoConfig)


def test_fal_config_discriminator_routes_to_kling_o3_pro_reference_to_video_config() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)

    parsed = adapter.validate_python(
        {
            "app_id": "fal-ai/kling-video/o3/pro/reference-to-video",
            "prompt": "@Element1 enters the scene.",
            "elements": [{"frontal_image_url": "https://example.com/front.png"}],
        }
    )

    assert isinstance(parsed, KlingVideoO3ProReferenceToVideoConfig)


def test_fal_config_discriminator_routes_to_kling_o3_4k_reference_to_video_config() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)

    parsed = adapter.validate_python(
        {
            "app_id": "fal-ai/kling-video/o3/4k/reference-to-video",
            "prompt": "@Image1 sets the style.",
            "image_urls": ["https://example.com/style.png"],
        }
    )

    assert isinstance(parsed, KlingVideoO34kReferenceToVideoConfig)


def test_fal_config_discriminator_routes_to_kling_o3_pro_video_to_video_edit_config() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)

    parsed = adapter.validate_python(
        {
            "app_id": "fal-ai/kling-video/o3/pro/video-to-video/edit",
            "prompt": "Replace the background with snow.",
            "video_url": "https://example.com/source.mp4",
        }
    )

    assert isinstance(parsed, KlingVideoO3ProVideoToVideoEditConfig)


def test_fal_config_discriminator_routes_to_happy_horse_text_to_video_config() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)

    parsed = adapter.validate_python(
        {
            "app_id": "alibaba/happy-horse/text-to-video",
            "prompt": "A cinematic city street fills with morning light.",
        }
    )

    assert isinstance(parsed, HappyHorseTextToVideoConfig)


def test_fal_config_discriminator_routes_to_luma_ray_3_2_text_to_video_config() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)

    parsed = adapter.validate_python(
        {
            "app_id": "luma/agent/ray/v3.2/text-to-video",
            "prompt": "A cinematic city street fills with morning light.",
        }
    )

    assert isinstance(parsed, LumaRay32TextToVideoConfig)


def test_fal_config_discriminator_routes_to_luma_ray_3_2_image_to_video_config() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)

    parsed = adapter.validate_python(
        {
            "app_id": "luma/agent/ray/v3.2/image-to-video",
            "prompt": "The subject slowly turns toward the camera.",
            "image_url": "https://example.com/start.png",
        }
    )

    assert isinstance(parsed, LumaRay32ImageToVideoConfig)


def test_fal_config_discriminator_routes_to_luma_ray_3_2_video_to_video_config() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)

    parsed = adapter.validate_python(
        {
            "app_id": "luma/agent/ray/v3.2/video-to-video",
            "prompt": "Replace the background with snow.",
            "video_url": "https://example.com/source.mp4",
        }
    )

    assert isinstance(parsed, LumaRay32VideoToVideoConfig)


def test_fal_config_discriminator_routes_to_luma_ray_3_2_reframe_config() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)

    parsed = adapter.validate_python(
        {
            "app_id": "luma/agent/ray/v3.2/reframe",
            "prompt": "Extend the scene into widescreen.",
            "video_url": "https://example.com/source.mp4",
            "aspect_ratio": "21:9",
        }
    )

    assert isinstance(parsed, LumaRay32ReframeConfig)


def test_fal_config_discriminator_routes_to_happy_horse_image_to_video_config() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)

    parsed = adapter.validate_python(
        {
            "app_id": "alibaba/happy-horse/image-to-video",
            "image_url": "https://example.com/start.png",
        }
    )

    assert isinstance(parsed, HappyHorseImageToVideoConfig)


def test_fal_config_discriminator_routes_to_happy_horse_reference_to_video_config() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)

    parsed = adapter.validate_python(
        {
            "app_id": "alibaba/happy-horse/reference-to-video",
            "prompt": "Animate character1.",
            "image_urls": ["https://example.com/character.png"],
        }
    )

    assert isinstance(parsed, HappyHorseReferenceToVideoConfig)


def test_fal_config_discriminator_routes_to_veo3_1_text_to_video_config() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)

    parsed = adapter.validate_python(
        {
            "app_id": "fal-ai/veo3.1",
            "prompt": "A cinematic city street fills with morning light.",
        }
    )

    assert isinstance(parsed, Veo31TextToVideoConfig)


def test_fal_config_discriminator_routes_to_veo3_1_image_to_video_config() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)

    parsed = adapter.validate_python(
        {
            "app_id": "fal-ai/veo3.1/image-to-video",
            "prompt": "The subject slowly turns toward the camera.",
            "image_url": "https://example.com/start.png",
        }
    )

    assert isinstance(parsed, Veo31ImageToVideoConfig)


def test_fal_config_discriminator_routes_to_veo3_1_first_last_frame_to_video_config() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)

    parsed = adapter.validate_python(
        {
            "app_id": "fal-ai/veo3.1/first-last-frame-to-video",
            "prompt": "Animate between the first and last frames.",
            "first_frame_url": "https://example.com/first.png",
            "last_frame_url": "https://example.com/last.png",
        }
    )

    assert isinstance(parsed, Veo31FirstLastFrameToVideoConfig)


def test_fal_config_discriminator_routes_to_veo3_1_reference_to_video_config() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)

    parsed = adapter.validate_python(
        {
            "app_id": "fal-ai/veo3.1/reference-to-video",
            "prompt": "Animate the reference images.",
            "image_urls": ["https://example.com/ref.png"],
        }
    )

    assert isinstance(parsed, Veo31ReferenceToVideoConfig)


def test_fal_config_discriminator_routes_to_vidu_q3_text_to_video_config() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)

    parsed = adapter.validate_python(
        {
            "app_id": "fal-ai/vidu/q3/text-to-video",
            "prompt": "A cinematic city street fills with morning light.",
        }
    )

    assert isinstance(parsed, ViduQ3TextToVideoConfig)


def test_fal_config_discriminator_routes_to_vidu_q3_image_to_video_config() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)

    parsed = adapter.validate_python(
        {
            "app_id": "fal-ai/vidu/q3/image-to-video",
            "image_url": "https://example.com/start.png",
        }
    )

    assert isinstance(parsed, ViduQ3ImageToVideoConfig)


def test_fal_config_discriminator_routes_to_vidu_q3_reference_to_video_config() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)

    parsed = adapter.validate_python(
        {
            "app_id": "fal-ai/vidu/q3/reference-to-video",
            "prompt": "Animate the reference images.",
            "reference_image_urls": ["https://example.com/ref.png"],
        }
    )

    assert isinstance(parsed, ViduQ3ReferenceToVideoConfig)


def test_fal_config_discriminator_routes_to_vidu_q3_reference_to_video_mix_config() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)

    parsed = adapter.validate_python(
        {
            "app_id": "fal-ai/vidu/q3/reference-to-video/mix",
            "prompt": "Animate the reference images.",
            "reference_image_urls": ["https://example.com/ref.png"],
        }
    )

    assert isinstance(parsed, ViduQ3ReferenceToVideoMixConfig)


def test_fal_config_discriminator_routes_to_sam_3_1_image_config() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)

    parsed = adapter.validate_python(
        {
            "app_id": "fal-ai/sam-3-1/image",
            "image_url": "https://example.com/truck.jpg",
        }
    )

    assert isinstance(parsed, Sam31ImageConfig)


def test_fal_config_discriminator_routes_to_sam_3_1_image_rle_config() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)

    parsed = adapter.validate_python(
        {
            "app_id": "fal-ai/sam-3-1/image-rle",
            "image_url": "https://example.com/truck.jpg",
        }
    )

    assert isinstance(parsed, Sam31ImageRleConfig)


def test_fal_config_discriminator_routes_to_sam_3_1_video_config() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)

    parsed = adapter.validate_python(
        {
            "app_id": "fal-ai/sam-3-1/video",
            "video_url": "https://example.com/source.mp4",
        }
    )

    assert isinstance(parsed, Sam31VideoConfig)


def test_fal_config_discriminator_routes_to_sam_3_1_video_rle_config() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)

    parsed = adapter.validate_python(
        {
            "app_id": "fal-ai/sam-3-1/video-rle",
            "video_url": "https://example.com/source.mp4",
        }
    )

    assert isinstance(parsed, Sam31VideoRleConfig)


def test_fal_config_discriminator_routes_to_happy_horse_video_edit_config() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)

    parsed = adapter.validate_python(
        {
            "app_id": "alibaba/happy-horse/video-edit",
            "video_url": "https://example.com/source.mp4",
            "prompt": "Recolor the sky to a deep purple sunset.",
        }
    )

    assert isinstance(parsed, HappyHorseVideoEditConfig)
