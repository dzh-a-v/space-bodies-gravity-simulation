import random
from itertools import combinations

import numpy as np

from gravity_sim.core.body import Body
from gravity_sim.core.constants import MIN_MASS, MIN_RADIUS
from gravity_sim.core.vector import distance
from gravity_sim.physics.fragmentation import (
    FRAGMENT_TARGET_VOLUME_FRACTION,
    create_fragments,
    merge_bodies,
)


def fragment_volume_fraction(parent: Body, fragments: list[Body]) -> float:
    return sum(fragment.volume for fragment in fragments) / parent.volume


def test_fragmentation_conserves_mass_and_names_fragments():
    parent = Body("Parent", 9e15, 9e3, [0, 0, 0], [0, 0, 0])

    fragments = create_fragments(parent, 3, set())

    assert len(fragments) == 3
    assert np.isclose(sum(fragment.mass for fragment in fragments), parent.mass)
    assert all(fragment.name.startswith("Parent_fragment_") for fragment in fragments)
    assert all(fragment.is_fragment for fragment in fragments)
    assert {fragment.fragment_origin for fragment in fragments} == {"Parent"}


def test_existing_fragment_cannot_fragment_again():
    parent = Body("Fragment", 9e15, 9e3, [0, 0, 0], [0, 0, 0], is_fragment=True)

    assert create_fragments(parent, 3, set()) == []


def test_available_slots_truncate_fragment_count():
    parent = Body("Parent", 9e15, 9e3, [0, 0, 0], [0, 0, 0])

    fragments = create_fragments(parent, 10, set(), available_slots=3)

    assert len(fragments) == 3
    assert np.isclose(sum(fragment.mass for fragment in fragments), parent.mass)


def test_fragment_count_is_limited_by_minimum_fragment_mass():
    parent = Body("Parent", 3e15, 9e3, [0, 0, 0], [0, 0, 0])

    fragments = create_fragments(parent, 10, set())

    assert len(fragments) == 3
    assert all(fragment.mass >= MIN_MASS for fragment in fragments)
    assert np.isclose(sum(fragment.mass for fragment in fragments), parent.mass)


def test_fragment_count_can_drop_below_requested_minimum_for_mass_limit():
    parent = Body("Parent", 3e15, 9e3, [0, 0, 0], [0, 0, 0])

    fragments = create_fragments(parent, 4, set(), minimum=4)

    assert len(fragments) == 3
    assert all(fragment.mass >= MIN_MASS for fragment in fragments)


def test_minimum_fragmentable_mass_can_create_two_fragments():
    parent = Body("Parent", 2e15, 9e3, [0, 0, 0], [0, 0, 0])

    fragments = create_fragments(parent, 4, set(), minimum=4)

    assert len(fragments) == 2
    assert all(fragment.mass >= MIN_MASS for fragment in fragments)


def test_fragments_spawn_at_random_positions_inside_parent():
    parent = Body("Parent", 9e20, 1e6, [10, 20, 30], [0, 0, 0])

    fragments = create_fragments(parent, 8, set(), rng=random.Random(0))

    assert all(
        distance(fragment.position, parent.position) + fragment.radius <= parent.radius
        for fragment in fragments
    )
    assert len({tuple(fragment.position) for fragment in fragments}) == len(fragments)


def test_fragment_positions_depend_on_rng_seed():
    parent = Body("Parent", 9e20, 1e6, [0, 0, 0], [0, 0, 0])

    first = create_fragments(parent, 8, set(), rng=random.Random(0))
    second = create_fragments(parent, 8, set(), rng=random.Random(1))

    assert any(
        not np.allclose(left.position, right.position)
        for left, right in zip(first, second, strict=True)
    )


def test_fragment_total_volume_does_not_exceed_target_fraction():
    parent = Body("Parent", 9e20, 1e6, [0, 0, 0], [0, 0, 0])

    fragments = create_fragments(parent, 8, set(), rng=random.Random(0))

    assert fragments
    assert fragment_volume_fraction(parent, fragments) <= FRAGMENT_TARGET_VOLUME_FRACTION


def test_fragment_radius_scales_with_parent_radius():
    small_parent = Body("Small", 9e20, 1e6, [0, 0, 0], [0, 0, 0])
    large_parent = Body("Large", 9e20, 2e6, [0, 0, 0], [0, 0, 0])

    small_fragments = create_fragments(small_parent, 8, set(), rng=random.Random(0))
    large_fragments = create_fragments(large_parent, 8, set(), rng=random.Random(0))

    assert small_fragments
    assert large_fragments
    assert np.isclose(
        large_fragments[0].radius / small_fragments[0].radius,
        large_parent.radius / small_parent.radius,
        rtol=0.05,
    )


def test_fragment_radius_decreases_when_fragment_count_grows():
    parent = Body("Parent", 9e20, 1e6, [0, 0, 0], [0, 0, 0])

    few_fragments = create_fragments(parent, 4, set(), rng=random.Random(0))
    many_fragments = create_fragments(parent, 12, set(), rng=random.Random(0))

    assert few_fragments
    assert many_fragments
    assert few_fragments[0].radius > many_fragments[0].radius


def test_fragments_do_not_touch_each_other():
    parent = Body("Parent", 9e20, 1e6, [0, 0, 0], [0, 0, 0])

    fragments = create_fragments(parent, 8, set(), rng=random.Random(0))

    assert fragments
    for left, right in combinations(fragments, 2):
        assert distance(left.position, right.position) > left.radius + right.radius


def test_fragmentation_returns_empty_when_minimum_radius_cannot_fit():
    parent = Body("Parent", 2e15, MIN_RADIUS, [0, 0, 0], [0, 0, 0])

    assert create_fragments(parent, 2, set(), rng=random.Random(0)) == []


def test_fragment_copy_preserves_origin():
    fragment = Body(
        "Fragment",
        9e15,
        9e3,
        [0, 0, 0],
        [0, 0, 0],
        is_fragment=True,
        fragment_origin="Parent",
    )

    assert fragment.copy().fragment_origin == "Parent"


def test_merge_preserves_shared_fragment_origin():
    left = Body(
        "Left",
        3e15,
        1e3,
        [0, 0, 0],
        [0, 0, 0],
        is_fragment=True,
        fragment_origin="Parent",
    )
    right = Body(
        "Right",
        3e15,
        1e3,
        [0, 0, 0],
        [0, 0, 0],
        is_fragment=True,
        fragment_origin="Parent",
    )

    assert merge_bodies(left, right).fragment_origin == "Parent"


def test_merge_clears_mixed_fragment_origin():
    fragment = Body(
        "Fragment",
        3e15,
        1e3,
        [0, 0, 0],
        [0, 0, 0],
        is_fragment=True,
        fragment_origin="Parent",
    )
    body = Body("Body", 3e15, 1e3, [0, 0, 0], [0, 0, 0])
    other_fragment = Body(
        "Other",
        3e15,
        1e3,
        [0, 0, 0],
        [0, 0, 0],
        is_fragment=True,
        fragment_origin="OtherParent",
    )

    assert merge_bodies(fragment, body).fragment_origin is None
    assert merge_bodies(fragment, other_fragment).fragment_origin is None
