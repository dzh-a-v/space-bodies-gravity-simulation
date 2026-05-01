import random

from gravity_sim.core.body import Body
from gravity_sim.core.system_state import SimulationSettings
from gravity_sim.physics.collisions import candidate_collision_pairs, resolve_collisions


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


def test_spatial_hash_keeps_nearby_candidates_and_drops_distant_pairs():
    bodies = [
        Body("A", 1e20, 1e4, [0, 0, 0], [0, 0, 0]),
        Body("B", 1e20, 1e4, [1.5e4, 0, 0], [0, 0, 0]),
        Body("C", 1e20, 1e4, [1e9, 0, 0], [0, 0, 0]),
    ]

    pairs = candidate_collision_pairs(bodies)

    assert (0, 1) in pairs
    assert (0, 2) not in pairs
    assert (1, 2) not in pairs
