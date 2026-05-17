import random
from math import isclose

from gravity_sim.core.body import Body
from gravity_sim.core.system_state import SimulationSettings
from gravity_sim.core.vector import distance, norm
from gravity_sim.physics.collisions import resolve_collisions
from gravity_sim.physics.fragmentation import (
    COLLISION_SPREAD_DEADZONE_RADIUS_FRACTION,
    COLLISION_SPREAD_SPEED_FRACTION,
    apply_collision_spread_impulse,
)


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
        direction_to_large = (large.position - fragment.position) / fragment_distances[fragment.name]
        expected_x_impulse = max_impulse_speed * expected_strength * direction_to_large[0]
        actual_x_impulse = fragment.velocity[0] - small.velocity[0]

        assert isclose(
            actual_x_impulse,
            expected_x_impulse,
            rel_tol=1e-12,
            abs_tol=1e-9,
        )

    nearest_fragment = min(small_fragments, key=lambda body: fragment_distances[body.name])
    farthest_fragment = max(small_fragments, key=lambda body: fragment_distances[body.name])
    nearest_direction = (
        large.position - nearest_fragment.position
    ) / fragment_distances[nearest_fragment.name]
    assert isclose(
        nearest_fragment.velocity[0] - small.velocity[0],
        max_impulse_speed * nearest_direction[0],
        rel_tol=1e-12,
    )
    assert farthest_fragment.velocity[0] - small.velocity[0] == 0.0


def test_collision_spread_impulse_leaves_central_fragments_unchanged():
    parent = Body("Parent", 1e16, 1e3, [0, 0, 0], [100, 0, 0])
    partner = Body("Partner", 1e16, 1e3, [1e4, 0, 0], [-100, 0, 0])
    central = Body("Central", 1e15, 1e3, [0, 0, 0], parent.velocity.copy())
    near_central = Body("Near", 1e15, 1e3, [0, 100, 0], parent.velocity.copy())
    side = Body("Side", 1e15, 1e3, [0, 1e3, 0], parent.velocity.copy())

    apply_collision_spread_impulse(parent, partner, [central, near_central, side])

    assert norm(central.velocity - parent.velocity) == 0.0
    assert norm(near_central.velocity - parent.velocity) == 0.0
    assert side.velocity[1] > parent.velocity[1]
    assert side.velocity[0] == parent.velocity[0]


def test_collision_spread_impulse_strength_grows_linearly_with_lateral_distance():
    parent = Body("Parent", 1e16, 1e3, [0, 0, 0], [100, 0, 0])
    partner = Body("Partner", 1e16, 1e3, [1e4, 0, 0], [-100, 0, 0])
    middle = Body("Middle", 1e15, 1e3, [0, 500, 0], parent.velocity.copy())
    side = Body("Side", 1e15, 1e3, [0, 1e3, 0], parent.velocity.copy())

    apply_collision_spread_impulse(parent, partner, [middle, side])

    max_spread_speed = norm(parent.velocity - partner.velocity) * COLLISION_SPREAD_SPEED_FRACTION
    deadzone_radius = parent.radius * COLLISION_SPREAD_DEADZONE_RADIUS_FRACTION
    expected_middle_strength = (500.0 - deadzone_radius) / (1000.0 - deadzone_radius)

    assert isclose(
        norm(middle.velocity - parent.velocity),
        max_spread_speed * expected_middle_strength,
        rel_tol=1e-12,
    )
    assert isclose(norm(side.velocity - parent.velocity), max_spread_speed, rel_tol=1e-12)


def test_collision_spread_impulse_applies_per_parent_axis():
    left = Body("Left", 1e16, 1e3, [0, 0, 0], [100, 0, 0])
    right = Body("Right", 1e16, 1e3, [1e4, 0, 0], [-100, 0, 0])
    left_fragment = Body("LeftFragment", 1e15, 1e3, [0, 1e3, 0], left.velocity.copy())
    right_fragment = Body("RightFragment", 1e15, 1e3, [1e4, 1e3, 0], right.velocity.copy())

    apply_collision_spread_impulse(left, right, [left_fragment])
    apply_collision_spread_impulse(right, left, [right_fragment])

    assert left_fragment.velocity[1] > left.velocity[1]
    assert right_fragment.velocity[1] > right.velocity[1]
