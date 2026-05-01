"""Physics backends for exact Newtonian integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np
from numpy.typing import NDArray

from gravity_sim.core.constants import GRAVITATIONAL_CONSTANT
from gravity_sim.core.snapshot import SimulationSnapshot


@dataclass(slots=True)
class StepResult:
    snapshot: SimulationSnapshot
    backend_name: str


class PhysicsBackend(Protocol):
    name: str

    def compute_accelerations(self, snapshot: SimulationSnapshot) -> NDArray[np.float64]:
        """Return acceleration array shaped as (N, 3)."""

    def step(self, snapshot: SimulationSnapshot, dt: float) -> StepResult:
        """Advance positions and velocities with Velocity Verlet."""


class PythonBackend:
    """Vectorized exact O(n^2) fallback backend."""

    name = "python-vectorized"

    def __init__(self, block_size: int = 512) -> None:
        self.block_size = block_size

    def compute_accelerations(self, snapshot: SimulationSnapshot) -> NDArray[np.float64]:
        return compute_accelerations_numpy(snapshot.masses, snapshot.positions, self.block_size)

    def step(self, snapshot: SimulationSnapshot, dt: float) -> StepResult:
        if dt <= 0 or snapshot.body_count == 0:
            return StepResult(snapshot.copy(), self.name)

        old_accelerations = self.compute_accelerations(snapshot)
        next_snapshot = snapshot.copy()
        next_snapshot.accelerations = old_accelerations
        next_snapshot.positions = (
            snapshot.positions
            + snapshot.velocities * dt
            + 0.5 * old_accelerations * dt**2
        )

        new_accelerations = self.compute_accelerations(next_snapshot)
        next_snapshot.velocities = snapshot.velocities + 0.5 * (
            old_accelerations + new_accelerations
        ) * dt
        next_snapshot.accelerations = new_accelerations
        return StepResult(next_snapshot, self.name)


class CppExactBackend(PythonBackend):
    """Exact C++ backend loaded when the optional extension is available."""

    name = "cpp-exact"

    def __init__(self) -> None:
        super().__init__()
        self._native = _load_native_backend()
        if self._native is None:
            raise RuntimeError("C++ backend is not available.")

    @staticmethod
    def is_available() -> bool:
        return _load_native_backend() is not None

    def compute_accelerations(self, snapshot: SimulationSnapshot) -> NDArray[np.float64]:
        return self._native.compute_accelerations(
            snapshot.masses,
            snapshot.positions,
            GRAVITATIONAL_CONSTANT,
        )

    def step(self, snapshot: SimulationSnapshot, dt: float) -> StepResult:
        if dt <= 0 or snapshot.body_count == 0:
            return StepResult(snapshot.copy(), self.name)

        positions, velocities, accelerations = self._native.step_exact(
            snapshot.masses,
            snapshot.positions,
            snapshot.velocities,
            dt,
            GRAVITATIONAL_CONSTANT,
        )
        next_snapshot = snapshot.copy()
        next_snapshot.positions = positions
        next_snapshot.velocities = velocities
        next_snapshot.accelerations = accelerations
        return StepResult(next_snapshot, self.name)


_NATIVE_BACKEND = None
_NATIVE_IMPORT_ATTEMPTED = False


def _load_native_backend():
    global _NATIVE_BACKEND, _NATIVE_IMPORT_ATTEMPTED
    if _NATIVE_IMPORT_ATTEMPTED:
        return _NATIVE_BACKEND

    _NATIVE_IMPORT_ATTEMPTED = True
    try:
        from gravity_sim import _cpp_backend
    except ImportError:
        _NATIVE_BACKEND = None
    else:
        _NATIVE_BACKEND = _cpp_backend
    return _NATIVE_BACKEND


def create_best_backend() -> PhysicsBackend:
    if CppExactBackend.is_available():
        return CppExactBackend()
    return PythonBackend()


def compute_accelerations_numpy(
    masses: NDArray[np.float64],
    positions: NDArray[np.float64],
    block_size: int = 512,
) -> NDArray[np.float64]:
    body_count = len(masses)
    accelerations = np.zeros((body_count, 3), dtype=float)
    if body_count == 0:
        return accelerations

    for start in range(0, body_count, block_size):
        stop = min(start + block_size, body_count)
        delta = positions[np.newaxis, :, :] - positions[start:stop, np.newaxis, :]
        distance_squared = np.einsum("ijk,ijk->ij", delta, delta)
        with np.errstate(divide="ignore", invalid="ignore"):
            inverse_distance_cubed = np.where(
                distance_squared > 0.0,
                1.0 / (distance_squared * np.sqrt(distance_squared)),
                0.0,
            )
        weighted = (
            GRAVITATIONAL_CONSTANT
            * delta
            * masses[np.newaxis, :, np.newaxis]
            * inverse_distance_cubed[:, :, np.newaxis]
        )
        accelerations[start:stop] = weighted.sum(axis=1)

    return accelerations
