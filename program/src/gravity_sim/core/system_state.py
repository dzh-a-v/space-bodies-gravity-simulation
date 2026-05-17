"""Simulation state containers."""

from __future__ import annotations

from dataclasses import dataclass, field

from .body import Body
from .constants import FRAGMENT_OBJECT_LIMIT, MAX_FRAGMENTS, MIN_FRAGMENTS, MIN_ROCHE_FRAGMENTS

DEFAULT_TIME_STEP = 1.0
DEFAULT_TIME_SCALE = 100.0


@dataclass(slots=True)
class SimulationSettings:
    time_step: float = DEFAULT_TIME_STEP
    time_scale: float = DEFAULT_TIME_SCALE
    fragment_count: int = 8
    roche_fragment_count: int = 8
    max_objects: int = FRAGMENT_OBJECT_LIMIT
    artificial_coefficients_enabled: bool = True

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
                roche_fragment_count=self.settings.roche_fragment_count,
                max_objects=self.settings.max_objects,
                artificial_coefficients_enabled=(
                    self.settings.artificial_coefficients_enabled
                ),
            ),
        )

    @property
    def body_names(self) -> set[str]:
        return {body.name for body in self.bodies}

    def clamp_fragment_count(self) -> None:
        self.settings.fragment_count = max(
            MIN_FRAGMENTS,
            min(MAX_FRAGMENTS, self.settings.fragment_count),
        )
        self.settings.roche_fragment_count = max(
            MIN_ROCHE_FRAGMENTS,
            min(MAX_FRAGMENTS, self.settings.roche_fragment_count),
        )
