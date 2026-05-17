import random

from gravity_sim.core.body import Body
from gravity_sim.core.system_state import SimulationSettings
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


def test_attractor_side_fragments_get_extra_attraction():
    large = Body("Large", 1e17, 1e4, [0, 0, 0], [1e5, 0, 0])
    small = Body("Small", 2e16, 1e4, [2e4, 0, 0], [-1e5, 0, 0])

    result = resolve_collisions(
        [large, small],
        SimulationSettings(fragment_count=8),
        random.Random(0),
    )

    small_fragments = [body for body in result if body.name.startswith("Small_fragment")]
    attractor_side = [
        fragment for fragment in small_fragments if fragment.position[0] < small.position[0]
    ]
    far_side = [
        fragment for fragment in small_fragments if fragment.position[0] >= small.position[0]
    ]
    boosted = [
        fragment for fragment in small_fragments if fragment.velocity[0] < small.velocity[0]
    ]
    unchanged = [
        fragment for fragment in small_fragments if fragment.velocity[0] == small.velocity[0]
    ]

    assert len(attractor_side) == len(boosted) == 4
    assert len(far_side) == len(unchanged) == 4
    assert {fragment.name for fragment in boosted} == {
        fragment.name for fragment in attractor_side
    }
    assert {fragment.name for fragment in unchanged} == {
        fragment.name for fragment in far_side
    }
    assert all(fragment.acceleration[0] < 0.0 for fragment in boosted)
