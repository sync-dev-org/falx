from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field

from falx.models import BaseFalConfig

BriaFibo2AspectRatio = Literal[
    "1:1",
    "1:2",
    "1:3",
    "1:4",
    "1:5",
    "2:1",
    "2:3",
    "3:1",
    "3:2",
    "3:4",
    "4:1",
    "4:3",
    "4:5",
    "5:1",
    "5:4",
    "9:16",
    "9:21",
    "10:16",
    "16:9",
    "16:10",
    "21:9",
]


class BriaFibo2PromptObject(BaseModel):
    description: str | None = Field(
        default=None,
        description="A description of the object to be generated.",
    )
    location: str | None = Field(
        default=None,
        description="The location of the object in the image.",
    )
    relationship: str = Field(
        ...,
        description="The relationship of the object to other objects in the image.",
    )
    relative_size: str | None = Field(
        default=None,
        description="The relative size of the object in the image.",
    )
    shape_and_color: str | None = Field(
        default=None,
        description="The shape and color of the object.",
    )
    texture: str | None = Field(
        default=None,
        description="The texture of the object.",
    )
    appearance_details: str | None = Field(
        default=None,
        description="The appearance details of the object.",
    )
    number_of_objects: int | None = Field(
        default=None,
        description="The number of objects in the image.",
    )
    pose: str | None = Field(
        default=None,
        description="The pose of the object in the image.",
    )
    expression: str | None = Field(
        default=None,
        description="The expression of the object in the image.",
    )
    clothing: str | None = Field(
        default=None,
        description="The clothing of the object in the image.",
    )
    action: str | None = Field(
        default=None,
        description="The action of the object in the image.",
    )
    gender: str | None = Field(
        default=None,
        description="The gender of the object in the image.",
    )
    skin_tone_and_texture: str | None = Field(
        default=None,
        description="The skin tone and texture of the object in the image.",
    )
    orientation: str | None = Field(
        default=None,
        description="The orientation of the object in the image.",
    )


class BriaFibo2TextRender(BaseModel):
    text: str = Field(
        ...,
        description=(
            "The text to render. fibo-2 is also shown an image of it, so it renders as written."
        ),
    )
    location: str | None = Field(
        default=None,
        description="Where the text sits in the image.",
    )
    size: str | None = Field(
        default=None,
        description="The size of the text in the image.",
    )
    color: str | None = Field(
        default=None,
        description="The color of the text.",
    )
    font: str | None = Field(
        default=None,
        description="The style of the font.",
    )
    appearance_details: str | None = Field(
        default=None,
        description="Any other notable visual details of the text.",
    )


class BriaFibo2Aesthetics(BaseModel):
    composition: str | None = Field(
        default=None,
        description="The composition of the image to be generated.",
    )
    color_scheme: str | None = Field(
        default=None,
        description="The color scheme of the image to be generated.",
    )
    mood_atmosphere: str | None = Field(
        default=None,
        description="The mood and atmosphere of the image to be generated.",
    )


class BriaFibo2PhotographicCharacteristics(BaseModel):
    depth_of_field: str | None = Field(
        default=None,
        description="The depth of field in the image to be generated.",
    )
    focus: str | None = Field(
        default=None,
        description="The focus in the image to be generated.",
    )
    camera_angle: str | None = Field(
        default=None,
        description="The angle of the camera in the image to be generated.",
    )
    lens_focal_length: str | None = Field(
        default=None,
        description="The focal length of the lens in the image to be generated.",
    )


class BriaFibo2Lighting(BaseModel):
    conditions: str | None = Field(
        default=None,
        description="The conditions of the lighting in the image to be generated.",
    )
    direction: str | None = Field(
        default=None,
        description="The direction of the lighting in the image to be generated.",
    )
    shadows: str | None = Field(
        default=None,
        description="The shadows in the image to be generated.",
    )


class BriaFibo2Vgl(BaseModel):
    short_description: str | None = Field(
        default=None,
        description="A short description of the image to be generated.",
    )
    objects: list[BriaFibo2PromptObject] | None = Field(
        default=[],
        description=(
            "A list of objects in the image to be generated, along with their "
            "attributes and relationships to other objects in the image."
        ),
    )
    background_setting: str | None = Field(
        default=None,
        description="The background setting of the image to be generated.",
    )
    lighting: BriaFibo2Lighting | None = Field(
        default=None,
        description="The lighting of the image to be generated.",
    )
    aesthetics: BriaFibo2Aesthetics | None = Field(
        default=None,
        description="The aesthetics of the image to be generated.",
    )
    photographic_characteristics: BriaFibo2PhotographicCharacteristics | None = Field(
        default=None,
        description="The photographic characteristics of the image to be generated.",
    )
    style_medium: str | None = Field(
        default=None,
        description="The style medium of the image to be generated.",
    )
    text_render: list[BriaFibo2TextRender] | None = Field(
        default=[],
        description="A list of text to be rendered in the image.",
    )
    context: str | None = Field(
        default=None,
        description="The context of the image to be generated.",
    )
    artistic_style: str | None = Field(
        default=None,
        description="The artistic style of the image to be generated.",
    )


class BriaFibo2VglEdit(BriaFibo2Vgl):
    model_config = ConfigDict(extra="allow")

    edit_instruction: str | None = Field(
        default=None,
        description="The edit instruction for the image.",
    )


class BriaFibo2BaseConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    seed: int = Field(
        default=5555,
        le=2147483647,
        ge=0,
        description="Random seed for reproducibility, 0 to 2147483647.",
    )
    sync_mode: bool = Field(
        default=False,
        description="If true, returns the image directly in the response (increases latency).",
    )
