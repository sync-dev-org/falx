from __future__ import annotations

from typing import ClassVar, Literal, Self

from pydantic import Field, model_validator

from falx.models import BaseFalConfig


class IdolConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    app_id: Literal["speridlabs/idol"]
    image_url: str = Field(
        ...,
        description="URL of the image of a single object to convert into a 3D Gaussian splat.",
    )
    image_type: Literal["synthetic", "real"] = Field(
        default="synthetic",
        description=(
            "Kind of input image. `synthetic` for renders and generated images (tight crop), "
            "`real` for photographs (looser crop)."
        ),
    )
    num_gaussians: int = Field(
        default=262_144,
        ge=32_768,
        le=1_048_576,
        description=(
            "Target number of Gaussians in the output splat. Rounded down to a multiple of 32."
        ),
    )
    num_inference_steps: int = Field(
        default=50,
        ge=1,
        le=50,
        description="Number of sampling steps. Fewer are faster but lose some detail.",
    )
    guidance_scale: float = Field(
        default=3,
        ge=0,
        le=10,
        description="Classifier-free guidance: how strictly the object follows the image.",
    )
    seed: int | None = Field(
        default=None,
        description="Random seed for reproducibility. If None, a random seed is generated.",
    )
    enable_safety_checker: bool = Field(
        default=True,
        description="Enable safety checking of the input image.",
    )


class IdolMaxConfig(IdolConfig):
    app_id: Literal["speridlabs/idol/max", "speridlabs/idol/max/turbo"]
    image_url: str = Field(
        ...,
        description="URL of the image of a single object to convert into a game-ready 3D mesh.",
    )
    enable_pbr: bool = Field(
        default=False,
        description=(
            "Add roughness and metallic maps to the game-ready mesh with a TRELLIS.2 "
            "retexture of the preprocessed image; the base color is not changed. Adds "
            "typically 20 seconds to 2 minutes."
        ),
    )
    rig: bool = Field(
        default=False,
        description=(
            "Also return `rigged_character_glb`: the game-ready mesh with a skeleton and "
            "skin weights from SkinTokens, for characters and creatures (bipeds, quadrupeds, "
            "winged or tailed). `game_glb` stays without a skeleton. Rigid props such as "
            "chests get an unusable skeleton. Adds about 15 seconds (about 60 more on a "
            "runner's first such request, which loads the model)."
        ),
    )
    animations: list[Literal["walk", "run", "jump", "idle"]] = Field(
        default=[],
        description=(
            "Looping clips to write into `rigged_character_glb` as glTF animations; each "
            "is also returned alone in a file of the result's `animations`. Requires `rig`. "
            "Each is a hand-made animation of a human or of a four-legged animal, played "
            "in place on the limbs found from the skeleton and the skin; a clip the skeleton "
            "cannot play (walk, run and jump need two legs, or three or four on an animal) "
            "is left out, see `rig.animations` in the result."
        ),
    )
    mesh_resolution: Literal[128, 256, 512, 768, 1024, 1536] = Field(
        default=1024,
        description=(
            "Surface detail. The surface is fused from rendered splat depth on a grid "
            "of 0.75 x this many voxels along the object's longest side (1024 -> 768), "
            "capped near 80M voxels for bulky objects. Lower values are faster and coarser; "
            "above 1024 mostly adds time."
        ),
    )
    enable_usdz: bool = Field(
        default=False,
        description=(
            "Also return the game-ready mesh as a USDZ file (`game_usdz`), for AR Quick Look "
            "and USD pipelines: same geometry and textures, without a skeleton."
        ),
    )

    @model_validator(mode="after")
    def validate_animation_rig(self) -> Self:
        if self.animations and not self.rig:
            raise ValueError("animations require rig to be true")
        return self
