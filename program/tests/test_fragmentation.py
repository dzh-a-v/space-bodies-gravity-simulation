import numpy as np

from gravity_sim.core.body import Body
from gravity_sim.physics.fragmentation import create_fragments


def test_fragmentation_conserves_mass_and_names_fragments():
    parent = Body("Parent", 9e15, 9e3, [0, 0, 0], [0, 0, 0])

    fragments = create_fragments(parent, 3, set())

    assert len(fragments) == 3
    assert np.isclose(sum(fragment.mass for fragment in fragments), parent.mass)
    assert all(fragment.name.startswith("Parent_fragment_") for fragment in fragments)
    assert all(fragment.is_fragment for fragment in fragments)


def test_existing_fragment_cannot_fragment_again():
    parent = Body("Fragment", 9e15, 9e3, [0, 0, 0], [0, 0, 0], is_fragment=True)

    assert create_fragments(parent, 3, set()) == []


def test_available_slots_truncate_fragment_count():
    parent = Body("Parent", 9e15, 9e3, [0, 0, 0], [0, 0, 0])

    fragments = create_fragments(parent, 10, set(), available_slots=3)

    assert len(fragments) == 3
    assert np.isclose(sum(fragment.mass for fragment in fragments), parent.mass)
