"""High-level simulation engine."""

from __future__ import annotations

import random

from gravity_sim.core.body import Body
from gravity_sim.core.system_state import SimulationSettings, SystemState
from gravity_sim.core.validation import validate_bodies, validate_fragment_count

from .collisions import resolve_collisions
from .gravity import DirectGravitySolver, GravitySolver
from .integrators import velocity_verlet_step
from .roche import apply_roche_limit


class SimulationEngine:
    def __init__(
        self,
        state: SystemState | None = None,
        solver: GravitySolver | None = None,
        rng: random.Random | None = None,
    ) -> None:
        self.state = state or SystemState()
        self.solver = solver or DirectGravitySolver()
        self.rng = rng or random.Random()
        self._initial_state = self.state.copy()

    def set_bodies(self, bodies: list[Body]) -> None:
        self.state.bodies = validate_bodies(bodies)
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

        velocity_verlet_step(self.state.bodies, dt, self.solver)
        self.state.bodies = resolve_collisions(self.state.bodies, self.state.settings, self.rng)
        self.state.bodies = apply_roche_limit(self.state.bodies, self.state.settings, dt)
        self.recompute_accelerations()
        self.state.time_seconds += dt
        return self.state

    def recompute_accelerations(self) -> None:
        accelerations = self.solver.compute_accelerations(self.state.bodies)
        for body, acceleration in zip(self.state.bodies, accelerations, strict=True):
            body.acceleration = acceleration


def create_default_engine() -> SimulationEngine:
    return SimulationEngine(SystemState(settings=SimulationSettings()))
