"""Array-oriented simulation state used by fast physics backends."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from .body import Body
from .colors import Color


@dataclass(slots=True)
class SimulationSnapshot:
    names: list[str]
    masses: NDArray[np.float64]
    radii: NDArray[np.float64]
    positions: NDArray[np.float64]
    velocities: NDArray[np.float64]
    accelerations: NDArray[np.float64]
    is_fragment: NDArray[np.bool_]
    colors: list[Color | None]
    roche_exposure_seconds: list[dict[str, float]]

    @property
    def body_count(self) -> int:
        return len(self.names)

    def copy(self) -> "SimulationSnapshot":
        return SimulationSnapshot(
            names=list(self.names),
            masses=self.masses.copy(),
            radii=self.radii.copy(),
            positions=self.positions.copy(),
            velocities=self.velocities.copy(),
            accelerations=self.accelerations.copy(),
            is_fragment=self.is_fragment.copy(),
            colors=list(self.colors),
            roche_exposure_seconds=[dict(exposure) for exposure in self.roche_exposure_seconds],
        )


def bodies_to_snapshot(bodies: list[Body]) -> SimulationSnapshot:
    return SimulationSnapshot(
        names=[body.name for body in bodies],
        masses=np.array([body.mass for body in bodies], dtype=float),
        radii=np.array([body.radius for body in bodies], dtype=float),
        positions=np.array([body.position for body in bodies], dtype=float).reshape((-1, 3)),
        velocities=np.array([body.velocity for body in bodies], dtype=float).reshape((-1, 3)),
        accelerations=np.array([body.acceleration for body in bodies], dtype=float).reshape((-1, 3)),
        is_fragment=np.array([body.is_fragment for body in bodies], dtype=bool),
        colors=[body.color for body in bodies],
        roche_exposure_seconds=[dict(body.roche_exposure_seconds) for body in bodies],
    )


def snapshot_to_bodies(snapshot: SimulationSnapshot, bodies: list[Body]) -> None:
    if len(bodies) != snapshot.body_count:
        raise ValueError("Snapshot and body list sizes do not match.")

    for index, body in enumerate(bodies):
        body.mass = float(snapshot.masses[index])
        body.radius = float(snapshot.radii[index])
        body.position = snapshot.positions[index].copy()
        body.velocity = snapshot.velocities[index].copy()
        body.acceleration = snapshot.accelerations[index].copy()
        body.is_fragment = bool(snapshot.is_fragment[index])
        body.color = snapshot.colors[index]
        body.roche_exposure_seconds = dict(snapshot.roche_exposure_seconds[index])
