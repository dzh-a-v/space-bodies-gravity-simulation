"""High-level simulation engine."""

from __future__ import annotations

import random

from gravity_sim.core.body import Body
from gravity_sim.core.colors import initial_palette
from gravity_sim.core.snapshot import bodies_to_snapshot, snapshot_to_bodies
from gravity_sim.core.system_state import SimulationSettings, SystemState
from gravity_sim.core.validation import validate_bodies, validate_fragment_count

from .backends import PhysicsBackend, create_best_backend
from .collisions import resolve_collisions
from .roche import apply_roche_limit


class SimulationEngine:
    def __init__(
        self,
        state: SystemState | None = None,
        backend: PhysicsBackend | None = None,
        rng: random.Random | None = None,
    ) -> None:
        self.state = state or SystemState()
        self.backend = backend or create_best_backend()
        self.rng = rng or random.Random()
        self._initial_state = self.state.copy()

    def set_bodies(self, bodies: list[Body]) -> None:
        self.state.bodies = validate_bodies(bodies)
        self._assign_initial_colors()
        self.state.time_seconds = 0.0
        self._initial_state = self.state.copy()
        self.recompute_accelerations()

    def reset(self) -> None:
        settings = self.state.settings
        self.state = self._initial_state.copy()
        self.state.settings = settings
        self.recompute_accelerations()

    def step(self, dt: float | None = None) -> SystemState:
        validate_fragment_count(self.state.settings.fragment_count)
        dt = self.state.settings.effective_step() if dt is None else dt
        if dt <= 0:
            return self.state

        snapshot = bodies_to_snapshot(self.state.bodies)
        step_result = self.backend.step(snapshot, dt)
        snapshot_to_bodies(step_result.snapshot, self.state.bodies)

        before_events = _body_identity_signature(self.state.bodies)
        after_collisions = resolve_collisions(self.state.bodies, self.state.settings, self.rng)
        after_roche = apply_roche_limit(after_collisions, self.state.settings, dt)
        after_events = _body_identity_signature(after_roche)
        self.state.bodies = after_roche

        if before_events != after_events:
            self.recompute_accelerations()

        self.state.time_seconds += dt
        return self.state

    def recompute_accelerations(self) -> None:
        snapshot = bodies_to_snapshot(self.state.bodies)
        accelerations = self.backend.compute_accelerations(snapshot)
        for body, acceleration in zip(self.state.bodies, accelerations, strict=True):
            body.acceleration = acceleration

    def _assign_initial_colors(self) -> None:
        for body, color in zip(self.state.bodies, initial_palette(len(self.state.bodies)), strict=True):
            body.color = color


def create_default_engine() -> SimulationEngine:
    return SimulationEngine(SystemState(settings=SimulationSettings()))


def _body_identity_signature(bodies: list[Body]) -> tuple[int, ...]:
    return tuple(id(body) for body in bodies)
