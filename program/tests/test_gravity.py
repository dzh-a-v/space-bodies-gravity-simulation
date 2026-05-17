import numpy as np

from gravity_sim.core.body import Body
from gravity_sim.core.constants import GRAVITATIONAL_CONSTANT
from gravity_sim.physics.gravity import FRAGMENT_SELF_GRAVITY_SCALE, DirectGravitySolver


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


def test_same_origin_fragment_gravity_is_scaled_down():
    left = Body(
        "A",
        1e20,
        1e6,
        [0, 0, 0],
        [0, 0, 0],
        is_fragment=True,
        fragment_origin="Parent",
    )
    right = Body(
        "B",
        2e20,
        1e6,
        [1e7, 0, 0],
        [0, 0, 0],
        is_fragment=True,
        fragment_origin="Parent",
    )

    accelerations = DirectGravitySolver().compute_accelerations([left, right])

    assert np.isclose(
        accelerations[0][0],
        FRAGMENT_SELF_GRAVITY_SCALE * GRAVITATIONAL_CONSTANT * right.mass / 1e14,
    )
    assert np.isclose(
        accelerations[1][0],
        -FRAGMENT_SELF_GRAVITY_SCALE * GRAVITATIONAL_CONSTANT * left.mass / 1e14,
    )


def test_same_origin_fragment_gravity_is_unscaled_when_artificial_coefficients_are_off():
    left = Body(
        "A",
        1e20,
        1e6,
        [0, 0, 0],
        [0, 0, 0],
        is_fragment=True,
        fragment_origin="Parent",
    )
    right = Body(
        "B",
        2e20,
        1e6,
        [1e7, 0, 0],
        [0, 0, 0],
        is_fragment=True,
        fragment_origin="Parent",
    )

    accelerations = DirectGravitySolver(
        artificial_coefficients_enabled=False
    ).compute_accelerations([left, right])

    assert np.isclose(accelerations[0][0], GRAVITATIONAL_CONSTANT * right.mass / 1e14)
    assert np.isclose(accelerations[1][0], -GRAVITATIONAL_CONSTANT * left.mass / 1e14)


def test_different_origin_fragment_gravity_is_not_scaled():
    left = Body(
        "A",
        1e20,
        1e6,
        [0, 0, 0],
        [0, 0, 0],
        is_fragment=True,
        fragment_origin="Parent",
    )
    right = Body(
        "B",
        2e20,
        1e6,
        [1e7, 0, 0],
        [0, 0, 0],
        is_fragment=True,
        fragment_origin="OtherParent",
    )

    accelerations = DirectGravitySolver().compute_accelerations([left, right])

    assert np.isclose(accelerations[0][0], GRAVITATIONAL_CONSTANT * right.mass / 1e14)
    assert np.isclose(accelerations[1][0], -GRAVITATIONAL_CONSTANT * left.mass / 1e14)


def test_fragment_body_gravity_is_not_scaled():
    fragment = Body(
        "Fragment",
        1e20,
        1e6,
        [0, 0, 0],
        [0, 0, 0],
        is_fragment=True,
        fragment_origin="Parent",
    )
    body = Body("Body", 2e20, 1e6, [1e7, 0, 0], [0, 0, 0])

    accelerations = DirectGravitySolver().compute_accelerations([fragment, body])

    assert np.isclose(accelerations[0][0], GRAVITATIONAL_CONSTANT * body.mass / 1e14)
    assert np.isclose(accelerations[1][0], -GRAVITATIONAL_CONSTANT * fragment.mass / 1e14)
