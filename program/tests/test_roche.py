from math import isclose

from gravity_sim.core.body import Body
from gravity_sim.core.constants import ROCHE_REQUIRED_SECONDS
from gravity_sim.core.system_state import SimulationSettings
from gravity_sim.core.vector import distance, norm
from gravity_sim.physics.roche import apply_roche_limit, roche_limit


def test_roche_exposure_accumulates_and_fragments_after_24_hours():
    primary = Body("Primary", 1e21, 1e6, [0, 0, 0], [0, 0, 0])
    satellite = Body("Satellite", 4e15, 1e4, [1e6, 0, 0], [0, 0, 0])
    assert 1e6 <= roche_limit(primary, satellite)

    bodies = apply_roche_limit(
        [primary, satellite],
        SimulationSettings(fragment_count=4),
        ROCHE_REQUIRED_SECONDS / 2,
    )

    assert len(bodies) == 2
    assert bodies[1].roche_exposure_seconds["Primary"] == ROCHE_REQUIRED_SECONDS / 2

    bodies = apply_roche_limit(
        bodies,
        SimulationSettings(fragment_count=4),
        ROCHE_REQUIRED_SECONDS / 2,
    )

    assert len(bodies) == 5
    assert bodies[0].name == "Primary"
    assert all(body.is_fragment for body in bodies[1:])


def test_roche_exposure_resets_outside_limit():
    primary = Body("Primary", 1e20, 1e6, [0, 0, 0], [0, 0, 0])
    satellite = Body("Satellite", 2e15, 1e4, [1e6, 0, 0], [0, 0, 0])

    bodies = apply_roche_limit([primary, satellite], SimulationSettings(fragment_count=4), 3600)
    bodies[1].position[0] = 1e9
    bodies = apply_roche_limit(bodies, SimulationSettings(fragment_count=4), 3600)

    assert bodies[1].roche_exposure_seconds == {}


def test_roche_fragmentation_applies_distance_weighted_primary_impulse():
    primary = Body("Primary", 1e22, 1e6, [0, 0, 0], [0, 0, 0])
    satellite = Body("Satellite", 8e15, 1e4, [2e6, 0, 0], [0, 1000, 0])
    assert 2e6 <= roche_limit(primary, satellite)

    bodies = apply_roche_limit(
        [primary, satellite],
        SimulationSettings(fragment_count=8),
        ROCHE_REQUIRED_SECONDS,
    )

    fragments = [body for body in bodies if body.name.startswith("Satellite_fragment")]
    fragment_distances = {
        fragment.name: distance(fragment.position, primary.position)
        for fragment in fragments
    }
    nearest_distance = min(fragment_distances.values())
    farthest_distance = max(fragment_distances.values())
    distance_span = farthest_distance - nearest_distance
    max_impulse_speed = norm(satellite.velocity - primary.velocity) * 0.5

    for fragment in fragments:
        expected_strength = (
            farthest_distance - fragment_distances[fragment.name]
        ) / distance_span
        actual_impulse_speed = norm(fragment.velocity - satellite.velocity)

        assert isclose(
            actual_impulse_speed,
            max_impulse_speed * expected_strength,
            rel_tol=1e-12,
            abs_tol=1e-9,
        )

    nearest_fragment = min(fragments, key=lambda body: fragment_distances[body.name])
    farthest_fragment = max(fragments, key=lambda body: fragment_distances[body.name])
    assert isclose(
        norm(nearest_fragment.velocity - satellite.velocity),
        max_impulse_speed,
        rel_tol=1e-12,
    )
    assert norm(farthest_fragment.velocity - satellite.velocity) == 0.0


def test_roche_fragments_keep_parent_velocity_when_artificial_coefficients_are_off():
    primary = Body("Primary", 1e22, 1e6, [0, 0, 0], [0, 0, 0])
    satellite = Body("Satellite", 8e15, 1e4, [2e6, 0, 0], [0, 1000, 0])
    assert 2e6 <= roche_limit(primary, satellite)

    bodies = apply_roche_limit(
        [primary, satellite],
        SimulationSettings(
            fragment_count=8,
            artificial_coefficients_enabled=False,
        ),
        ROCHE_REQUIRED_SECONDS,
    )

    fragments = [body for body in bodies if body.name.startswith("Satellite_fragment")]
    assert fragments
    assert all(norm(fragment.velocity - satellite.velocity) == 0.0 for fragment in fragments)


def test_roche_keeps_body_when_minimum_valid_fragment_mass_is_impossible():
    primary = Body("Primary", 1e22, 1e6, [0, 0, 0], [0, 0, 0])
    satellite = Body("Satellite", 1.5e15, 1e4, [2e6, 0, 0], [0, 0, 0])
    assert 2e6 <= roche_limit(primary, satellite)

    bodies = apply_roche_limit(
        [primary, satellite],
        SimulationSettings(fragment_count=4),
        ROCHE_REQUIRED_SECONDS,
    )

    assert len(bodies) == 2
    assert bodies[0] is primary
    assert bodies[1] is satellite
    assert not bodies[1].is_fragment


def test_roche_minimum_fragmentable_mass_creates_two_fragments():
    primary = Body("Primary", 1e22, 1e6, [0, 0, 0], [0, 0, 0])
    satellite = Body("Satellite", 2e15, 1e4, [2e6, 0, 0], [0, 0, 0])
    assert 2e6 <= roche_limit(primary, satellite)

    bodies = apply_roche_limit(
        [primary, satellite],
        SimulationSettings(fragment_count=4),
        ROCHE_REQUIRED_SECONDS,
    )

    fragments = [body for body in bodies if body.name.startswith("Satellite_fragment")]
    assert len(fragments) == 2
    assert all(fragment.is_fragment for fragment in fragments)
