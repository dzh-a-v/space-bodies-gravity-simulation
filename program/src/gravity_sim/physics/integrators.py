"""Numerical integrators for simulation steps."""

from __future__ import annotations

from gravity_sim.core.body import Body

from .gravity import GravitySolver


def velocity_verlet_step(bodies: list[Body], dt: float, solver: GravitySolver) -> None:
    """Advance bodies in place using the Velocity Verlet method."""

    if dt <= 0 or not bodies:
        return

    old_accelerations = solver.compute_accelerations(bodies)

    for body, acceleration in zip(bodies, old_accelerations, strict=True):
        body.acceleration = acceleration
        body.position = body.position + body.velocity * dt + 0.5 * acceleration * dt**2

    new_accelerations = solver.compute_accelerations(bodies)

    for body, old_acceleration, new_acceleration in zip(
        bodies,
        old_accelerations,
        new_accelerations,
        strict=True,
    ):
        body.velocity = body.velocity + 0.5 * (old_acceleration + new_acceleration) * dt
        body.acceleration = new_acceleration
