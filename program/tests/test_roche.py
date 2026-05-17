from gravity_sim.core.body import Body
from gravity_sim.core.constants import ROCHE_REQUIRED_SECONDS
from gravity_sim.core.system_state import SimulationSettings
from gravity_sim.physics.roche import apply_roche_limit, roche_limit


def test_roche_exposure_accumulates_and_fragments_after_24_hours():
    primary = Body("Primary", 1e20, 1e6, [0, 0, 0], [0, 0, 0])
    satellite = Body("Satellite", 2e15, 1e4, [1e6, 0, 0], [0, 0, 0])
    assert 1e6 <= roche_limit(primary, satellite)

    bodies = apply_roche_limit(
        [primary, satellite],
        SimulationSettings(fragment_count=4),
        ROCHE_REQUIRED_SECONDS / 2,
    )

    assert len(bodies) == 2
    assert bodies[1].roche_exposure_seconds["Primary"] == ROCHE_REQUIRED_SECONDS / 2

    bodies = apply_roche_limit(
        bodies,
        SimulationSettings(fragment_count=4),
        ROCHE_REQUIRED_SECONDS / 2,
    )

    assert len(bodies) == 5
    assert bodies[0].name == "Primary"
    assert all(body.is_fragment for body in bodies[1:])


def test_roche_exposure_resets_outside_limit():
    primary = Body("Primary", 1e20, 1e6, [0, 0, 0], [0, 0, 0])
    satellite = Body("Satellite", 2e15, 1e4, [1e6, 0, 0], [0, 0, 0])

    bodies = apply_roche_limit([primary, satellite], SimulationSettings(fragment_count=4), 3600)
    bodies[1].position[0] = 1e9
    bodies = apply_roche_limit(bodies, SimulationSettings(fragment_count=4), 3600)

    assert bodies[1].roche_exposure_seconds == {}


def test_roche_fragmentation_applies_primary_impulse_to_attractor_side():
    primary = Body("Primary", 1e22, 1e6, [0, 0, 0], [0, 0, 0])
    satellite = Body("Satellite", 2e15, 1e4, [2e6, 0, 0], [0, 1000, 0])
    assert 2e6 <= roche_limit(primary, satellite)

    bodies = apply_roche_limit(
        [primary, satellite],
        SimulationSettings(fragment_count=8),
        ROCHE_REQUIRED_SECONDS,
    )

    fragments = [body for body in bodies if body.name.startswith("Satellite_fragment")]
    attractor_side = [
        fragment for fragment in fragments if fragment.position[0] < satellite.position[0]
    ]
    far_side = [
        fragment for fragment in fragments if fragment.position[0] >= satellite.position[0]
    ]
    boosted = [fragment for fragment in fragments if fragment.velocity[0] < 0.0]
    unchanged = [fragment for fragment in fragments if fragment.velocity[0] == 0.0]

    assert len(attractor_side) == len(boosted) == 4
    assert len(far_side) == len(unchanged) == 4
    assert {fragment.name for fragment in boosted} == {
        fragment.name for fragment in attractor_side
    }
    assert {fragment.name for fragment in unchanged} == {
        fragment.name for fragment in far_side
    }
