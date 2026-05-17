"""Texture assignment helpers for simulation bodies."""

from __future__ import annotations

from importlib import resources

Texture = str
TEXTURE_PACKAGE = "gravity_sim.resources.textures"


def available_planet_textures() -> tuple[Texture, ...]:
    root = resources.files(TEXTURE_PACKAGE)
    return tuple(sorted(item.name for item in root.iterdir() if item.name.endswith(".png")))
