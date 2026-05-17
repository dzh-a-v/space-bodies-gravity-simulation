import random

from gravity_sim.core.body import Body
from gravity_sim.core.colors import WHITE
from gravity_sim.core.system_state import SystemState
from gravity_sim.core.textures import PLANET_TEXTURES
from gravity_sim.physics.engine import SimulationEngine
from gravity_sim.physics.fragmentation import create_fragments, merge_bodies


def test_engine_assigns_unique_non_white_initial_colors():
    bodies = [
        Body("A", 1e20, 1e6, [0, 0, 0], [0, 0, 0]),
        Body("B", 1e20, 1e6, [1e7, 0, 0], [0, 0, 0]),
        Body("C", 1e20, 1e6, [0, 1e7, 0], [0, 0, 0]),
    ]

    engine = SimulationEngine(SystemState())
    engine.set_bodies(bodies)
    colors = [body.color for body in engine.state.bodies]

    assert len(colors) == len(set(colors))
    assert WHITE not in colors


def test_engine_assigns_random_texture_from_builtin_set():
    bodies = [
        Body("A", 1e20, 1e6, [0, 0, 0], [0, 0, 0]),
        Body("B", 1e20, 1e6, [1e7, 0, 0], [0, 0, 0]),
        Body("C", 1e20, 1e6, [0, 1e7, 0], [0, 0, 0]),
    ]

    engine = SimulationEngine(SystemState())
    engine.set_bodies(bodies)
    textures = [body.texture for body in engine.state.bodies]

    assert all(texture in PLANET_TEXTURES for texture in textures)


def test_texture_assignment_does_not_consume_physics_rng():
    engine = SimulationEngine(SystemState(), rng=random.Random(0))
    expected_next_random = random.Random(0).random()

    engine.set_bodies([Body("A", 1e20, 1e6, [0, 0, 0], [0, 0, 0])])

    assert engine.rng.random() == expected_next_random


def test_fragments_keep_parent_color():
    parent = Body("Parent", 9e15, 9e3, [0, 0, 0], [0, 0, 0], color=(10, 120, 240))

    fragments = create_fragments(parent, 3, set())

    assert {fragment.color for fragment in fragments} == {parent.color}


def test_fragments_keep_parent_texture():
    parent = Body("Parent", 9e15, 9e3, [0, 0, 0], [0, 0, 0], texture="planet_03.png")

    fragments = create_fragments(parent, 3, set())

    assert {fragment.texture for fragment in fragments} == {parent.texture}


def test_merged_body_is_white():
    left = Body("Left", 1e20, 1e6, [0, 0, 0], [0, 0, 0], color=(10, 120, 240))
    right = Body("Right", 1e20, 1e6, [0, 0, 0], [0, 0, 0], color=(240, 120, 10))

    merged = merge_bodies(left, right)

    assert merged.color == WHITE


def test_merged_body_drops_texture_so_white_color_is_visible():
    left = Body("Left", 2e20, 1e6, [0, 0, 0], [0, 0, 0], texture="planet_01.png")
    right = Body("Right", 1e20, 1e6, [0, 0, 0], [0, 0, 0], texture="planet_05.png")

    merged = merge_bodies(left, right)

    assert merged.color == WHITE
    assert merged.texture is None
