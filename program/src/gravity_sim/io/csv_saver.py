"""CSV scenario saving."""

from __future__ import annotations

import csv
from pathlib import Path

from gravity_sim.core.body import Body
from gravity_sim.core.validation import validate_bodies

from .csv_schema import CSV_COLUMNS


def save_bodies_to_csv(bodies: list[Body], path: str | Path) -> None:
    validate_bodies(bodies)
    path = Path(path)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for body in bodies:
            writer.writerow(
                {
                    "name": body.name,
                    "mass": body.mass,
                    "radius": body.radius,
                    "x": body.position[0],
                    "y": body.position[1],
                    "z": body.position[2],
                    "vx": body.velocity[0],
                    "vy": body.velocity[1],
                    "vz": body.velocity[2],
                    "ax": body.acceleration[0],
                    "ay": body.acceleration[1],
                    "az": body.acceleration[2],
                }
            )
