"""Texture assignment helpers for simulation bodies."""

from __future__ import annotations

from importlib import resources

Texture = str
TEXTURE_PACKAGE = "gravity_sim.resources.textures"
RESERVED_REAL_BODY_TEXTURES: frozenset[Texture] = frozenset(
    {
        "earth.png",
        "mars.png",
        "mercury.png",
        "venus.png",
    }
)


def available_planet_textures() -> tuple[Texture, ...]:
    root = resources.files(TEXTURE_PACKAGE)
    return tuple(
        sorted(
            item.name
            for item in root.iterdir()
            if item.name.endswith(".png") and item.name not in RESERVED_REAL_BODY_TEXTURES
        )
    )


def is_reserved_real_body_texture(texture: Texture | None) -> bool:
    return texture in RESERVED_REAL_BODY_TEXTURES
