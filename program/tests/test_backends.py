import numpy as np
import pytest

from gravity_sim.core.body import Body
from gravity_sim.core.snapshot import bodies_to_snapshot
from gravity_sim.physics.backends import CppExactBackend, PythonBackend, StepResult
from gravity_sim.physics.engine import SimulationEngine


def bodies():
    return [
        Body("A", 1e20, 1e6, [0, 0, 0], [0, 10, 0]),
        Body("B", 2e20, 1e6, [1e7, 0, 0], [0, -10, 0]),
        Body("C", 3e20, 1e6, [0, 1e7, 0], [-10, 0, 0]),
    ]


def test_snapshot_round_trip_updates_body_arrays():
    source = bodies()
    snapshot = bodies_to_snapshot(source)
    snapshot.positions += 1.0
    snapshot.velocities += 2.0

    from gravity_sim.core.snapshot import snapshot_to_bodies

    snapshot_to_bodies(snapshot, source)

    assert np.allclose(source[0].position, [1, 1, 1])
    assert np.allclose(source[1].velocity, [2, -8, 2])


def test_python_backend_step_is_deterministic():
    snapshot = bodies_to_snapshot(bodies())
    backend = PythonBackend(block_size=2)

    first = backend.step(snapshot, 60.0).snapshot
    second = backend.step(snapshot, 60.0).snapshot

    assert np.allclose(first.positions, second.positions)
    assert np.allclose(first.velocities, second.velocities)
    assert np.allclose(first.accelerations, second.accelerations)


def test_cpp_backend_matches_python_backend_when_available():
    if not CppExactBackend.is_available():
        pytest.skip("Optional C++ backend is not built in this environment.")

    snapshot = bodies_to_snapshot(bodies())
    python_result = PythonBackend(block_size=2).step(snapshot, 60.0).snapshot
    cpp_result = CppExactBackend().step(snapshot, 60.0).snapshot

    assert np.allclose(cpp_result.positions, python_result.positions)
    assert np.allclose(cpp_result.velocities, python_result.velocities)
    assert np.allclose(cpp_result.accelerations, python_result.accelerations)


class CountingBackend(PythonBackend):
    def __init__(self) -> None:
        super().__init__()
        self.compute_calls = 0
        self.step_calls = 0

    def compute_accelerations(self, snapshot):
        self.compute_calls += 1
        return np.zeros_like(snapshot.positions)

    def step(self, snapshot, dt):
        self.step_calls += 1
        next_snapshot = snapshot.copy()
        next_snapshot.positions = snapshot.positions + snapshot.velocities * dt
        next_snapshot.accelerations = np.zeros_like(snapshot.positions)
        return StepResult(next_snapshot, self.name)


def test_engine_does_not_recompute_after_step_without_events():
    backend = CountingBackend()
    engine = SimulationEngine(backend=backend)
    engine.set_bodies(
        [
            Body("A", 1e20, 1e3, [0, 0, 0], [1, 0, 0]),
            Body("B", 1e20, 1e3, [1e9, 0, 0], [0, 1, 0]),
        ]
    )

    assert backend.compute_calls == 1
    engine.step(60.0)

    assert backend.step_calls == 1
    assert backend.compute_calls == 1
