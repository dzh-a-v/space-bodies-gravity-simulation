from gravity_sim.core.body import Body
from gravity_sim.core.constants import ROCHE_REQUIRED_SECONDS
from gravity_sim.core.system_state import SimulationSettings
from gravity_sim.physics.roche import apply_roche_limit, candidate_roche_pairs_by_satellite, roche_limit


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


def test_roche_candidate_grid_keeps_nearby_heavier_primary_only():
    primary = Body("Primary", 1e20, 1e6, [0, 0, 0], [0, 0, 0])
    satellite = Body("Satellite", 2e15, 1e4, [1e6, 0, 0], [0, 0, 0])
    distant = Body("Distant", 1e21, 1e6, [1e12, 0, 0], [0, 0, 0])

    candidates = candidate_roche_pairs_by_satellite([primary, satellite, distant])

    assert candidates[1] == [0]
