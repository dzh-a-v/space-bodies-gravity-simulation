import random

from gravity_sim.core.body import Body
from gravity_sim.core.colors import WHITE
from gravity_sim.core.real_bodies import real_body_preset_for
from gravity_sim.core.system_state import SystemState
from gravity_sim.core.textures import RESERVED_REAL_BODY_TEXTURES, available_planet_textures
from gravity_sim.physics.engine import SimulationEngine
from gravity_sim.physics.fragmentation import create_fragments, merge_bodies


def test_available_planet_textures_are_discovered_from_resources():
    assert available_planet_textures() == ("1.png", "2.png", "3.png", "4.png", "5.png")
    assert not (set(available_planet_textures()) & RESERVED_REAL_BODY_TEXTURES)


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
    available_textures = available_planet_textures()

    assert all(texture in available_textures for texture in textures)


def test_engine_preserves_reserved_texture_for_real_body_preset():
    preset = real_body_preset_for("earth")
    body = Body(
        preset.name,
        preset.mass,
        preset.radius,
        [0, 0, 0],
        [0, 0, 0],
        texture="wrong.png",
        real_body_id=preset.id,
    )

    engine = SimulationEngine(SystemState())
    engine.set_bodies([body])

    assert engine.state.bodies[0].texture == "earth.png"


def test_engine_never_assigns_reserved_texture_to_custom_body():
    body = Body("Custom", 1e20, 1e6, [0, 0, 0], [0, 0, 0], texture="earth.png")

    engine = SimulationEngine(SystemState())
    engine.set_bodies([body])

    assert engine.state.bodies[0].texture in available_planet_textures()


def test_engine_assigns_unique_textures_when_possible():
    bodies = [
        Body("A", 1e20, 1e6, [0, 0, 0], [0, 0, 0]),
        Body("B", 1e20, 1e6, [1e7, 0, 0], [0, 0, 0]),
        Body("C", 1e20, 1e6, [0, 1e7, 0], [0, 0, 0]),
    ]

    engine = SimulationEngine(SystemState())
    engine.set_bodies(bodies)
    textures = [body.texture for body in engine.state.bodies]

    assert len(textures) < len(available_planet_textures())
    assert len(textures) == len(set(textures))


def test_engine_allows_repeated_textures_after_pool_is_exhausted():
    textures = available_planet_textures()
    bodies = [
        Body(f"Body {index}", 1e20, 1e6, [index * 1e7, 0, 0], [0, 0, 0])
        for index in range(len(textures) + 2)
    ]

    engine = SimulationEngine(SystemState())
    engine.set_bodies(bodies)
    assigned_textures = [body.texture for body in engine.state.bodies]

    assert all(texture in textures for texture in assigned_textures)
    assert len(set(assigned_textures)) == len(textures)


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
    parent = Body("Parent", 9e15, 9e3, [0, 0, 0], [0, 0, 0], texture="3.png")

    fragments = create_fragments(parent, 3, set())

    assert {fragment.texture for fragment in fragments} == {parent.texture}


def test_fragments_do_not_inherit_reserved_real_body_texture():
    parent = Body("Earth", 9e15, 9e3, [0, 0, 0], [0, 0, 0], texture="earth.png")

    fragments = create_fragments(parent, 3, set())

    assert {fragment.texture for fragment in fragments} == {None}


def test_merged_body_is_white():
    left = Body("Left", 1e20, 1e6, [0, 0, 0], [0, 0, 0], color=(10, 120, 240))
    right = Body("Right", 1e20, 1e6, [0, 0, 0], [0, 0, 0], color=(240, 120, 10))

    merged = merge_bodies(left, right)

    assert merged.color == WHITE


def test_merged_body_drops_texture_so_white_color_is_visible():
    left = Body("Left", 2e20, 1e6, [0, 0, 0], [0, 0, 0], texture="1.png")
    right = Body("Right", 1e20, 1e6, [0, 0, 0], [0, 0, 0], texture="5.png")

    merged = merge_bodies(left, right)

    assert merged.color == WHITE
    assert merged.texture is None


def test_engine_preserves_merged_body_white_without_texture():
    left = Body("Left", 2e20, 1e6, [0, 0, 0], [0, 0, 0], texture="1.png")
    right = Body("Right", 1e20, 1e6, [0, 0, 0], [0, 0, 0], texture="5.png")
    merged = merge_bodies(left, right)

    engine = SimulationEngine(SystemState())
    engine.set_bodies([merged])

    assert engine.state.bodies[0].color == WHITE
    assert engine.state.bodies[0].texture is None
