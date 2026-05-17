"""Built-in scenario presets."""

from __future__ import annotations

from importlib import resources
from pathlib import Path

from gravity_sim.core.body import Body
from gravity_sim.core.real_bodies import real_body_preset_named

from .csv_loader import load_bodies_from_csv

PRESET_PACKAGE = "gravity_sim.resources.presets"


def list_presets() -> list[str]:
    root = resources.files(PRESET_PACKAGE)
    return sorted(item.name for item in root.iterdir() if item.name.endswith(".csv"))


def load_preset(name: str) -> list[Body]:
    if not name.endswith(".csv"):
        name = f"{name}.csv"
    with resources.as_file(resources.files(PRESET_PACKAGE) / name) as path:
        bodies = load_bodies_from_csv(Path(path))

    for body in bodies:
        preset = real_body_preset_named(body.name)
        if preset is None:
            continue
        body.real_body_id = preset.id
        body.texture = preset.texture

    return bodies
