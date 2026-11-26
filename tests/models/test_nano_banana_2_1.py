from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import BaseFalConfig, config_class_for_app_id


@pytest.fixture(params=["google/nano-banana-2.1", "google/nano-banana-2.1/edit"])
def payload(request: pytest.FixtureRequest) -> dict[str, object]:
    result: dict[str, object] = {"app_id": request.param, "prompt": "a cat on a mat"}
    if request.param.endswith("/edit"):
        result["image_urls"] = ["https://example.com/input.png"]
    return result


def parse(payload: dict[str, object]) -> BaseFalConfig:
    config_class = config_class_for_app_id(str(payload["app_id"]))
    assert config_class is not None, f"{payload['app_id']} must be registered"
    return config_class.model_validate(payload)


def test_nano_banana_2_1_uses_api_defaults(payload: dict[str, object]) -> None:
    config = parse(payload)

    expected = {
        **payload,
        "num_images": 1,
        "limit_generations": True,
        "sync_mode": False,
        "system_prompt": "",
        "resolution": "1K",
        "aspect_ratio": "auto",
        "output_format": "png",
        "thinking_level": "medium",
        "safety_tolerance": "4",
        "enable_web_search": False,
        "seed": None,
    }
    if str(payload["app_id"]).endswith("/edit"):
        expected.update(video_url=None, pdf_url=None)
    assert config.model_dump() == expected


def test_nano_banana_2_1_preserves_explicit_parameters(payload: dict[str, object]) -> None:
    payload.update(
        num_images=4,
        limit_generations=False,
        sync_mode=True,
        system_prompt="Use a polished editorial illustration style.",
        resolution="4K",
        aspect_ratio="16:9",
        output_format="jpeg",
        thinking_level="high",
        safety_tolerance="6",
        enable_web_search=True,
        seed=-42,
    )
    if str(payload["app_id"]).endswith("/edit"):
        payload.update(
            video_url="https://example.com/video.mp4", pdf_url="data:application/pdf,doc"
        )

    assert parse(payload).model_dump() == payload


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("prompt", "ab"),
        ("prompt", "a" * 50001),
        ("system_prompt", "a" * 50001),
        ("num_images", 0),
        ("num_images", 5),
        ("num_images", "abc"),
        ("num_images", 1.5),
        ("resolution", "0.5K"),
        ("thinking_level", "low"),
        ("aspect_ratio", "1:2"),
        ("output_format", "jpg"),
        ("safety_tolerance", "0"),
        ("seed", "abc"),
        ("unexpected", True),
    ],
)
def test_nano_banana_2_1_rejects_values_outside_api_constraints(
    payload: dict[str, object], field_name: str, value: object
) -> None:
    payload[field_name] = value

    with pytest.raises(ValidationError, match=field_name):
        parse(payload)


def test_nano_banana_2_1_requires_prompt(payload: dict[str, object]) -> None:
    del payload["prompt"]

    with pytest.raises(ValidationError, match="prompt"):
        parse(payload)


@pytest.mark.parametrize("length", [3, 50000])
def test_nano_banana_2_1_accepts_prompt_length_boundaries(
    payload: dict[str, object], length: int
) -> None:
    payload["prompt"] = "a" * length

    assert parse(payload).prompt == payload["prompt"]


def test_nano_banana_2_1_accepts_maximum_system_prompt(payload: dict[str, object]) -> None:
    payload["system_prompt"] = "a" * 50000

    assert parse(payload).system_prompt == payload["system_prompt"]


@pytest.mark.parametrize(
    ("field_name", "values"),
    [
        ("thinking_level", ["minimal", "medium", "high", None]),
        ("resolution", ["1K", "2K", "4K"]),
        ("output_format", ["jpeg", "png", "webp"]),
        ("safety_tolerance", ["1", "2", "3", "4", "5", "6"]),
        (
            "aspect_ratio",
            [
                "auto",
                "21:9",
                "16:9",
                "3:2",
                "4:3",
                "5:4",
                "1:1",
                "4:5",
                "3:4",
                "2:3",
                "9:16",
                "4:1",
                "1:4",
                "8:1",
                "1:8",
                None,
            ],
        ),
    ],
)
def test_nano_banana_2_1_accepts_api_enum_values(
    payload: dict[str, object], field_name: str, values: list[object]
) -> None:
    for value in values:
        payload[field_name] = value
        assert getattr(parse(payload), field_name) == value


@pytest.mark.parametrize("field_name", ["image_urls", "video_url", "pdf_url", "audio_url"])
def test_nano_banana_2_1_text_to_image_rejects_edit_context(field_name: str) -> None:
    payload = {
        "app_id": "google/nano-banana-2.1",
        "prompt": "a cat on a mat",
        field_name: ["https://example.com/input.png"] if field_name == "image_urls" else "url",
    }

    with pytest.raises(ValidationError, match=field_name):
        parse(payload)
