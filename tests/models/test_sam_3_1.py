from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import (
    Sam31BoxPrompt,
    Sam31BoxPromptBase,
    Sam31ImageConfig,
    Sam31ImageRleConfig,
    Sam31PointPrompt,
    Sam31PointPromptBase,
    Sam31VideoConfig,
    Sam31VideoRleConfig,
)


def test_sam_3_1_image_accepts_schema_defaults() -> None:
    config = Sam31ImageConfig(
        app_id="fal-ai/sam-3-1/image",
        image_url="https://example.com/truck.jpg",
    )

    assert config.model_dump() == {
        "app_id": "fal-ai/sam-3-1/image",
        "image_url": "https://example.com/truck.jpg",
        "prompt": "wheel",
        "point_prompts": [],
        "box_prompts": [],
        "apply_mask": True,
        "sync_mode": False,
        "output_format": "png",
        "return_multiple_masks": False,
        "max_masks": 3,
        "include_scores": False,
        "include_boxes": False,
    }


def test_sam_3_1_image_accepts_all_fields() -> None:
    config = Sam31ImageConfig(
        app_id="fal-ai/sam-3-1/image",
        image_url="https://example.com/truck.jpg",
        prompt="person",
        point_prompts=[
            Sam31PointPrompt(x=100, y=200, label=1, object_id=1, frame_index=0),
        ],
        box_prompts=[
            Sam31BoxPrompt(x_min=10, y_min=20, x_max=110, y_max=220, object_id=1, frame_index=0),
        ],
        apply_mask=False,
        sync_mode=True,
        output_format="webp",
        return_multiple_masks=True,
        max_masks=10,
        include_scores=True,
        include_boxes=True,
    )

    assert config.max_masks == 10
    assert config.output_format == "webp"
    assert config.point_prompts[0].frame_index == 0


@pytest.mark.parametrize("invalid_max_masks", [0, 33])
def test_sam_3_1_image_rejects_max_masks_out_of_range(invalid_max_masks: int) -> None:
    with pytest.raises(ValidationError):
        Sam31ImageConfig(
            app_id="fal-ai/sam-3-1/image",
            image_url="https://example.com/truck.jpg",
            max_masks=invalid_max_masks,
        )


def test_sam_3_1_image_rejects_extra_field() -> None:
    with pytest.raises(ValidationError):
        Sam31ImageConfig(
            app_id="fal-ai/sam-3-1/image",
            image_url="https://example.com/truck.jpg",
            unknown_field=True,  # type: ignore[call-arg]
        )


def test_sam_3_1_image_rle_accepts_schema_defaults() -> None:
    config = Sam31ImageRleConfig(
        app_id="fal-ai/sam-3-1/image-rle",
        image_url="https://example.com/truck.jpg",
    )

    assert config.model_dump() == {
        "app_id": "fal-ai/sam-3-1/image-rle",
        "image_url": "https://example.com/truck.jpg",
        "prompt": "wheel",
        "point_prompts": [],
        "box_prompts": [],
        "apply_mask": True,
        "sync_mode": False,
        "output_format": "png",
        "return_multiple_masks": False,
        "max_masks": 3,
        "include_scores": False,
        "include_boxes": False,
    }


def test_sam_3_1_image_rle_accepts_point_prompt_with_frame_index() -> None:
    config = Sam31ImageRleConfig(
        app_id="fal-ai/sam-3-1/image-rle",
        image_url="https://example.com/truck.jpg",
        point_prompts=[Sam31PointPrompt(x=50, y=60, label=1, frame_index=2)],
    )

    assert config.point_prompts[0].frame_index == 2


def test_sam_3_1_video_accepts_schema_defaults() -> None:
    config = Sam31VideoConfig(
        app_id="fal-ai/sam-3-1/video",
        video_url="https://example.com/source.mp4",
    )

    assert config.model_dump() == {
        "app_id": "fal-ai/sam-3-1/video",
        "video_url": "https://example.com/source.mp4",
        "prompt": "",
        "point_prompts": [],
        "box_prompts": [],
        "apply_mask": True,
        "video_output_type": "X264 (.mp4)",
        "detection_threshold": 0.5,
        "max_num_objects": 16,
    }


def test_sam_3_1_video_accepts_point_prompts_base_without_frame_index() -> None:
    config = Sam31VideoConfig(
        app_id="fal-ai/sam-3-1/video",
        video_url="https://example.com/source.mp4",
        point_prompts=[Sam31PointPromptBase(x=100, y=200, label=1, object_id=1)],
    )

    assert config.point_prompts == [
        Sam31PointPromptBase(x=100, y=200, label=1, object_id=1),
    ]


def test_sam_3_1_video_rejects_point_prompt_base_with_frame_index() -> None:
    with pytest.raises(ValidationError):
        Sam31PointPromptBase(x=100, y=200, label=1, object_id=1, frame_index=0)  # type: ignore[call-arg]


def test_sam_3_1_video_rejects_box_prompt_base_with_frame_index() -> None:
    with pytest.raises(ValidationError):
        Sam31BoxPromptBase(  # type: ignore[call-arg]
            x_min=0,
            y_min=0,
            x_max=100,
            y_max=100,
            object_id=1,
            frame_index=0,
        )


@pytest.mark.parametrize("invalid_threshold", [0.05, 1.5])
def test_sam_3_1_video_rejects_detection_threshold_out_of_range(invalid_threshold: float) -> None:
    with pytest.raises(ValidationError):
        Sam31VideoConfig(
            app_id="fal-ai/sam-3-1/video",
            video_url="https://example.com/source.mp4",
            detection_threshold=invalid_threshold,
        )


@pytest.mark.parametrize("invalid_max_objects", [0, 129])
def test_sam_3_1_video_rejects_max_num_objects_out_of_range(invalid_max_objects: int) -> None:
    with pytest.raises(ValidationError):
        Sam31VideoConfig(
            app_id="fal-ai/sam-3-1/video",
            video_url="https://example.com/source.mp4",
            max_num_objects=invalid_max_objects,
        )


def test_sam_3_1_video_rle_accepts_schema_defaults() -> None:
    config = Sam31VideoRleConfig(
        app_id="fal-ai/sam-3-1/video-rle",
        video_url="https://example.com/source.mp4",
    )

    assert config.model_dump() == {
        "app_id": "fal-ai/sam-3-1/video-rle",
        "video_url": "https://example.com/source.mp4",
        "prompt": "",
        "point_prompts": [],
        "box_prompts": [],
        "apply_mask": False,
        "detection_threshold": 0.5,
        "max_num_objects": 16,
        "mask_url": None,
        "frame_index": 0,
        "boundingbox_zip": False,
        "return_object_rles": False,
    }


@pytest.mark.parametrize("return_object_rles", [True, False])
def test_sam_3_1_video_rle_accepts_per_object_mask_output(return_object_rles: bool) -> None:
    config = Sam31VideoRleConfig(
        app_id="fal-ai/sam-3-1/video-rle",
        video_url="https://example.com/source.mp4",
        return_object_rles=return_object_rles,
    )

    assert config.model_dump()["return_object_rles"] is return_object_rles


@pytest.mark.parametrize("invalid_return_object_rles", [None, "invalid"])
def test_sam_3_1_video_rle_rejects_invalid_per_object_mask_options(
    invalid_return_object_rles: object,
) -> None:
    with pytest.raises(ValidationError, match="return_object_rles") as exc_info:
        Sam31VideoRleConfig.model_validate(
            {
                "app_id": "fal-ai/sam-3-1/video-rle",
                "video_url": "https://example.com/source.mp4",
                "return_object_rles": invalid_return_object_rles,
            }
        )

    assert exc_info.value.errors()[0]["type"] in {"bool_type", "bool_parsing"}


def test_sam_3_1_video_rle_accepts_negative_initial_frame_index() -> None:
    config = Sam31VideoRleConfig(
        app_id="fal-ai/sam-3-1/video-rle",
        video_url="https://example.com/source.mp4",
        mask_url="https://example.com/mask.png",
        frame_index=-1,
    )

    assert config.model_dump()["frame_index"] == -1


def test_sam_3_1_video_rle_accepts_point_prompt_with_frame_index() -> None:
    config = Sam31VideoRleConfig(
        app_id="fal-ai/sam-3-1/video-rle",
        video_url="https://example.com/source.mp4",
        point_prompts=[Sam31PointPrompt(x=10, y=20, label=1, object_id=1, frame_index=5)],
    )

    assert config.point_prompts[0].frame_index == 5


def test_sam_3_1_video_rle_accepts_detection_threshold_at_minimum_0_01() -> None:
    config = Sam31VideoRleConfig(
        app_id="fal-ai/sam-3-1/video-rle",
        video_url="https://example.com/source.mp4",
        detection_threshold=0.01,
    )

    assert config.detection_threshold == 0.01


def test_sam_3_1_video_rle_rejects_detection_threshold_below_minimum() -> None:
    with pytest.raises(ValidationError):
        Sam31VideoRleConfig(
            app_id="fal-ai/sam-3-1/video-rle",
            video_url="https://example.com/source.mp4",
            detection_threshold=0.005,
        )


def test_sam_3_1_video_rle_accepts_mask_url_and_initial_frame_index() -> None:
    config = Sam31VideoRleConfig(
        app_id="fal-ai/sam-3-1/video-rle",
        video_url="https://example.com/source.mp4",
        mask_url="https://example.com/mask.png",
        frame_index=3,
        boundingbox_zip=True,
    )

    assert config.mask_url == "https://example.com/mask.png"
    assert config.frame_index == 3
    assert config.boundingbox_zip is True


def test_sam_3_1_point_prompt_rejects_extra_field() -> None:
    with pytest.raises(ValidationError):
        Sam31PointPrompt(x=1, y=2, label=1, unknown=True)  # type: ignore[call-arg]


def test_sam_3_1_box_prompt_rejects_extra_field() -> None:
    with pytest.raises(ValidationError):
        Sam31BoxPrompt(x_min=0, y_min=0, x_max=10, y_max=10, unknown=True)  # type: ignore[call-arg]


def test_sam_3_1_point_prompt_label_rejects_non_binary_value() -> None:
    with pytest.raises(ValidationError):
        Sam31PointPrompt(x=1, y=2, label=2)  # type: ignore[arg-type]
