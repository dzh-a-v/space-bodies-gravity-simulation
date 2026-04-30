"""Simulation state containers."""

from __future__ import annotations

from dataclasses import dataclass, field

from .body import Body
from .constants import FRAGMENT_OBJECT_LIMIT, MAX_FRAGMENTS


@dataclass(slots=True)
class SimulationSettings:
    time_step: float = 60.0
    time_scale: float = 1.0
    fragment_count: int = 8
    max_objects: int = FRAGMENT_OBJECT_LIMIT

    def effective_step(self) -> float:
        return self.time_step * self.time_scale


@dataclass(slots=True)
class SystemState:
    bodies: list[Body] = field(default_factory=list)
    time_seconds: float = 0.0
    settings: SimulationSettings = field(default_factory=SimulationSettings)

    def copy(self) -> "SystemState":
        return SystemState(
            bodies=[body.copy() for body in self.bodies],
            time_seconds=self.time_seconds,
            settings=SimulationSettings(
                time_step=self.settings.time_step,
                time_scale=self.settings.time_scale,
                fragment_count=self.settings.fragment_count,
                max_objects=self.settings.max_objects,
            ),
        )

    @property
    def body_names(self) -> set[str]:
        return {body.name for body in self.bodies}

    def clamp_fragment_count(self) -> None:
        self.settings.fragment_count = max(2, min(MAX_FRAGMENTS, self.settings.fragment_count))
