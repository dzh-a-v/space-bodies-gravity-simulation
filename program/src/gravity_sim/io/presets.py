"""Built-in scenario presets."""

from __future__ import annotations

from importlib import resources
from pathlib import Path

from gravity_sim.core.body import Body

from .csv_loader import load_bodies_from_csv

PRESET_PACKAGE = "gravity_sim.resources.presets"


def list_presets() -> list[str]:
    root = resources.files(PRESET_PACKAGE)
    return sorted(item.name for item in root.iterdir() if item.name.endswith(".csv"))


def load_preset(name: str) -> list[Body]:
    if not name.endswith(".csv"):
        name = f"{name}.csv"
    with resources.as_file(resources.files(PRESET_PACKAGE) / name) as path:
        return load_bodies_from_csv(Path(path))
