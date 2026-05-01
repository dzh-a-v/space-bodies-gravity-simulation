from gravity_sim.core.body import Body
from gravity_sim.core.colors import WHITE
from gravity_sim.core.system_state import SystemState
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


def test_fragments_keep_parent_color():
    parent = Body("Parent", 9e15, 9e3, [0, 0, 0], [0, 0, 0], color=(10, 120, 240))

    fragments = create_fragments(parent, 3, set())

    assert {fragment.color for fragment in fragments} == {parent.color}


def test_merged_body_is_white():
    left = Body("Left", 1e20, 1e6, [0, 0, 0], [0, 0, 0], color=(10, 120, 240))
    right = Body("Right", 1e20, 1e6, [0, 0, 0], [0, 0, 0], color=(240, 120, 10))

    merged = merge_bodies(left, right)

    assert merged.color == WHITE
