"""Roche-limit checks."""

from __future__ import annotations

import random

from gravity_sim.core.body import Body
from gravity_sim.core.constants import MIN_ROCHE_FRAGMENTS, ROCHE_REQUIRED_SECONDS
from gravity_sim.core.system_state import SimulationSettings
from gravity_sim.core.vector import distance

from .fragmentation import apply_attractor_impulse, can_fragment, create_fragments


def roche_limit(primary: Body, satellite: Body) -> float:
    return 2.9 * primary.radius * (primary.density / satellite.density) ** (1.0 / 3.0)


def apply_roche_limit(
    bodies: list[Body],
    settings: SimulationSettings,
    dt: float,
    rng: random.Random | None = None,
) -> list[Body]:
    if dt <= 0 or not bodies:
        return bodies

    rng = rng or random.Random()
    consumed: set[int] = set()
    additions: list[Body] = []

    for satellite_index, satellite in enumerate(bodies):
        if satellite_index in consumed or not can_fragment(satellite):
            continue

        active_primaries: set[str] = set()
        should_fragment = False
        fragmenting_primary: Body | None = None

        for primary_index, primary in enumerate(bodies):
            if primary_index == satellite_index or primary.mass <= satellite.mass:
                continue

            if distance(primary.position, satellite.position) <= roche_limit(primary, satellite):
                active_primaries.add(primary.name)
                satellite.roche_exposure_seconds[primary.name] = (
                    satellite.roche_exposure_seconds.get(primary.name, 0.0) + dt
                )
                if satellite.roche_exposure_seconds[primary.name] >= ROCHE_REQUIRED_SECONDS:
                    should_fragment = True
                    fragmenting_primary = primary
                    break

        for primary_name in list(satellite.roche_exposure_seconds):
            if primary_name not in active_primaries:
                del satellite.roche_exposure_seconds[primary_name]

        if not should_fragment:
            continue

        existing_after_removal = len(bodies) - len(consumed) - 1 + len(additions)
        available_slots = max(0, settings.max_objects - existing_after_removal)
        used_names = {
            body.name
            for index, body in enumerate(bodies)
            if index not in consumed and index != satellite_index
        }
        used_names.update(body.name for body in additions)
        fragments = create_fragments(
            satellite,
            settings.roche_fragment_count,
            used_names,
            available_slots=available_slots,
            minimum=MIN_ROCHE_FRAGMENTS,
            rng=rng,
        )
        if not fragments:
            continue

        consumed.add(satellite_index)
        if fragmenting_primary is not None:
            apply_attractor_impulse(satellite, fragmenting_primary, fragments)
        additions.extend(fragments)

    output = [body for index, body in enumerate(bodies) if index not in consumed]
    output.extend(additions)
    return output
