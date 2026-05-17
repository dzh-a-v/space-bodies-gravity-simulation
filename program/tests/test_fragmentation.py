import random

import numpy as np

from gravity_sim.core.body import Body
from gravity_sim.core.vector import distance
from gravity_sim.physics.fragmentation import create_fragments, merge_bodies


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


def test_fragments_spawn_at_random_positions_inside_parent():
    parent = Body("Parent", 9e15, 9e3, [10, 20, 30], [0, 0, 0])

    fragments = create_fragments(parent, 8, set(), rng=random.Random(0))

    assert all(distance(fragment.position, parent.position) <= parent.radius for fragment in fragments)
    assert len({tuple(fragment.position) for fragment in fragments}) == len(fragments)


def test_fragment_positions_depend_on_rng_seed():
    parent = Body("Parent", 9e15, 9e3, [0, 0, 0], [0, 0, 0])

    first = create_fragments(parent, 8, set(), rng=random.Random(0))
    second = create_fragments(parent, 8, set(), rng=random.Random(1))

    assert any(
        not np.allclose(left.position, right.position)
        for left, right in zip(first, second, strict=True)
    )


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
