"""Roche-limit checks."""

from __future__ import annotations

from gravity_sim.core.body import Body
from gravity_sim.core.constants import MIN_ROCHE_FRAGMENTS, ROCHE_REQUIRED_SECONDS
from gravity_sim.core.system_state import SimulationSettings
from gravity_sim.core.vector import distance

from .fragmentation import can_fragment, create_fragments


def roche_limit(primary: Body, satellite: Body) -> float:
    return 2.9 * primary.radius * (primary.density / satellite.density) ** (1.0 / 3.0)


def apply_roche_limit(
    bodies: list[Body],
    settings: SimulationSettings,
    dt: float,
) -> list[Body]:
    if dt <= 0 or not bodies:
        return bodies

    consumed: set[int] = set()
    additions: list[Body] = []

    for satellite_index, satellite in enumerate(bodies):
        if satellite_index in consumed or not can_fragment(satellite):
            continue

        active_primaries: set[str] = set()
        should_fragment = False

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
                    break

        for primary_name in list(satellite.roche_exposure_seconds):
            if primary_name not in active_primaries:
                del satellite.roche_exposure_seconds[primary_name]

        if not should_fragment:
            continue

        consumed.add(satellite_index)
        existing_after_removal = len(bodies) - len(consumed) + len(additions)
        available_slots = max(0, settings.max_objects - existing_after_removal)
        used_names = {body.name for index, body in enumerate(bodies) if index not in consumed}
        used_names.update(body.name for body in additions)
        fragment_count = max(settings.fragment_count, MIN_ROCHE_FRAGMENTS)
        additions.extend(
            create_fragments(
                satellite,
                fragment_count,
                used_names,
                available_slots=available_slots,
                minimum=MIN_ROCHE_FRAGMENTS,
            )
        )

    output = [body for index, body in enumerate(bodies) if index not in consumed]
    output.extend(additions)
    return output
