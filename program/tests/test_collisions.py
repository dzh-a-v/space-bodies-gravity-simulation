import random
from math import isclose

from gravity_sim.core.body import Body
from gravity_sim.core.system_state import SimulationSettings
from gravity_sim.core.vector import distance, norm
from gravity_sim.physics.collisions import resolve_collisions


def test_small_mass_ratio_collision_merges():
    big = Body("Big", 1e20, 1e6, [0, 0, 0], [0, 0, 0])
    small = Body("Small", 1e15, 1e5, [1.0e6, 0, 0], [0, 0, 0])

    result = resolve_collisions([big, small], SimulationSettings(fragment_count=4))

    assert len(result) == 1
    assert result[0].mass == big.mass + small.mass


def test_equal_fast_collision_fragments_both_bodies():
    left = Body("Left", 5e15, 1e4, [0, 0, 0], [1e5, 0, 0])
    right = Body("Right", 5e15, 1e4, [2e4, 0, 0], [-1e5, 0, 0])

    result = resolve_collisions(
        [left, right],
        SimulationSettings(fragment_count=2),
        random.Random(0),
    )

    assert len(result) == 4
    assert all(body.is_fragment for body in result)


def test_equal_slow_collision_merges():
    left = Body("Left", 5e15, 1e4, [0, 0, 0], [0, 0, 0])
    right = Body("Right", 5e15, 1e4, [2e4, 0, 0], [0, 0, 0])

    result = resolve_collisions([left, right], SimulationSettings(fragment_count=2))

    assert len(result) == 1
    assert result[0].mass == left.mass + right.mass


def test_fragments_get_distance_weighted_extra_attraction():
    large = Body("Large", 1e17, 1e4, [0, 0, 0], [1e5, 0, 0])
    small = Body("Small", 2e16, 1e4, [2e4, 0, 0], [-1e5, 0, 0])

    result = resolve_collisions(
        [large, small],
        SimulationSettings(fragment_count=8),
        random.Random(0),
    )

    small_fragments = [body for body in result if body.name.startswith("Small_fragment")]
    fragment_distances = {
        fragment.name: distance(fragment.position, large.position)
        for fragment in small_fragments
    }
    nearest_distance = min(fragment_distances.values())
    farthest_distance = max(fragment_distances.values())
    distance_span = farthest_distance - nearest_distance
    max_impulse_speed = norm(small.velocity - large.velocity) * 0.5

    for fragment in small_fragments:
        expected_strength = (
            farthest_distance - fragment_distances[fragment.name]
        ) / distance_span
        actual_impulse_speed = norm(fragment.velocity - small.velocity)

        assert isclose(
            actual_impulse_speed,
            max_impulse_speed * expected_strength,
            rel_tol=1e-12,
            abs_tol=1e-9,
        )

    nearest_fragment = min(small_fragments, key=lambda body: fragment_distances[body.name])
    farthest_fragment = max(small_fragments, key=lambda body: fragment_distances[body.name])
    assert isclose(
        norm(nearest_fragment.velocity - small.velocity),
        max_impulse_speed,
        rel_tol=1e-12,
    )
    assert norm(farthest_fragment.velocity - small.velocity) == 0.0
