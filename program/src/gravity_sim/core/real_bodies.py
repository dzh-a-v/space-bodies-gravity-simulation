"""Real rocky body presets available from the add-body dialog."""

from __future__ import annotations

from dataclasses import dataclass

from .textures import Texture


@dataclass(frozen=True, slots=True)
class RealBodyPreset:
    id: str
    name: str
    mass: float
    radius: float
    texture: Texture


REAL_BODY_PRESETS: tuple[RealBodyPreset, ...] = (
    RealBodyPreset("mercury", "Mercury", 3.3011e23, 2.4397e6, "mercury.png"),
    RealBodyPreset("venus", "Venus", 4.8675e24, 6.0518e6, "venus.png"),
    RealBodyPreset("earth", "Earth", 5.97237e24, 6.371e6, "earth.png"),
    RealBodyPreset("mars", "Mars", 6.4171e23, 3.3895e6, "mars.png"),
)

REAL_BODY_PRESETS_BY_ID = {preset.id: preset for preset in REAL_BODY_PRESETS}
REAL_BODY_PRESETS_BY_NAME = {
    preset.name.casefold(): preset for preset in REAL_BODY_PRESETS
}


def real_body_preset_for(preset_id: str | None) -> RealBodyPreset | None:
    if preset_id is None:
        return None
    return REAL_BODY_PRESETS_BY_ID.get(preset_id)


def real_body_preset_named(name: str) -> RealBodyPreset | None:
    return REAL_BODY_PRESETS_BY_NAME.get(name.strip().casefold())
