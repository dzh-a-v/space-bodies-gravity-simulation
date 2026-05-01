import numpy as np

from gravity_sim.core.body import Body
from gravity_sim.core.constants import GRAVITATIONAL_CONSTANT
from gravity_sim.core.snapshot import bodies_to_snapshot
from gravity_sim.physics.backends import PythonBackend
from gravity_sim.physics.gravity import DirectGravitySolver


def test_pairwise_gravity_direction_and_magnitude():
    left = Body("A", 1e20, 1e6, [0, 0, 0], [0, 0, 0])
    right = Body("B", 2e20, 1e6, [1e7, 0, 0], [0, 0, 0])

    accelerations = DirectGravitySolver().compute_accelerations([left, right])

    assert np.isclose(accelerations[0][0], GRAVITATIONAL_CONSTANT * right.mass / 1e14)
    assert np.isclose(accelerations[1][0], -GRAVITATIONAL_CONSTANT * left.mass / 1e14)
    assert accelerations[0][1] == 0
    assert accelerations[1][2] == 0


def test_zero_distance_does_not_create_nan():
    left = Body("A", 1e20, 1e6, [0, 0, 0], [0, 0, 0])
    right = Body("B", 2e20, 1e6, [0, 0, 0], [0, 0, 0])

    accelerations = DirectGravitySolver().compute_accelerations([left, right])

    assert np.all(np.isfinite(accelerations[0]))
    assert np.all(np.isfinite(accelerations[1]))
    assert np.allclose(accelerations[0], [0, 0, 0])
    assert np.allclose(accelerations[1], [0, 0, 0])


def test_vectorized_backend_matches_legacy_direct_solver():
    bodies = [
        Body("A", 1e20, 1e6, [0, 0, 0], [0, 0, 0]),
        Body("B", 2e20, 1e6, [1e7, 0, 0], [0, 0, 0]),
        Body("C", 3e20, 1e6, [0, 1e7, 0], [0, 0, 0]),
    ]

    legacy = DirectGravitySolver().compute_accelerations(bodies)
    vectorized = PythonBackend(block_size=2).compute_accelerations(bodies_to_snapshot(bodies))

    assert np.allclose(vectorized, legacy)
