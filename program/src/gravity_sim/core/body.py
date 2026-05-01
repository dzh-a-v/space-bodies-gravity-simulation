"""Simulation body model."""

from __future__ import annotations

from dataclasses import dataclass, field
from math import pi

from .colors import Color
from .vector import Vector3, vector3


@dataclass(slots=True)
class Body:
    name: str
    mass: float
    radius: float
    position: Vector3
    velocity: Vector3
    acceleration: Vector3 = field(default_factory=vector3)
    is_fragment: bool = False
    color: Color | None = None
    roche_exposure_seconds: dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.name = str(self.name).strip()
        self.mass = float(self.mass)
        self.radius = float(self.radius)
        self.position = vector3(self.position)
        self.velocity = vector3(self.velocity)
        self.acceleration = vector3(self.acceleration)

    @property
    def volume(self) -> float:
        return (4.0 / 3.0) * pi * self.radius**3

    @property
    def density(self) -> float:
        return self.mass / self.volume

    def copy(self) -> "Body":
        return Body(
            name=self.name,
            mass=self.mass,
            radius=self.radius,
            position=self.position.copy(),
            velocity=self.velocity.copy(),
            acceleration=self.acceleration.copy(),
            is_fragment=self.is_fragment,
            color=self.color,
            roche_exposure_seconds=dict(self.roche_exposure_seconds),
        )
