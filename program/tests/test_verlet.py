import numpy as np

from gravity_sim.core.body import Body
from gravity_sim.physics.integrators import velocity_verlet_step


class ZeroSolver:
    def compute_accelerations(self, bodies):
        return [np.zeros(3) for _ in bodies]


def test_velocity_verlet_keeps_constant_velocity_without_acceleration():
    body = Body("A", 1e20, 1e6, [0, 0, 0], [10, 0, 0])

    velocity_verlet_step([body], 2.0, ZeroSolver())

    assert np.allclose(body.position, [20, 0, 0])
    assert np.allclose(body.velocity, [10, 0, 0])
    assert np.allclose(body.acceleration, [0, 0, 0])
