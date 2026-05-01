"""Roche-limit checks."""

from __future__ import annotations

from collections import defaultdict
from itertools import product
from math import floor

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
    candidate_primaries = candidate_roche_pairs_by_satellite(bodies)

    for satellite_index, satellite in enumerate(bodies):
        if satellite_index in consumed or not can_fragment(satellite):
            continue

        active_primaries: set[str] = set()
        should_fragment = False

        for primary_index in candidate_primaries.get(satellite_index, ()):
            primary = bodies[primary_index]
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


def candidate_roche_pairs_by_satellite(bodies: list[Body]) -> dict[int, list[int]]:
    """Return conservative Roche candidates using a global exact upper bound."""

    if len(bodies) < 2:
        return {}

    max_limit = _max_possible_roche_limit(bodies)
    if max_limit <= 0:
        return {}

    cell_size = max(1.0, max_limit)
    grid: dict[tuple[int, int, int], list[int]] = defaultdict(list)
    for index, body in enumerate(bodies):
        grid[_cell_key(body, cell_size)].append(index)

    pairs: dict[int, set[int]] = defaultdict(set)
    for cell, indexes in grid.items():
        for offset in product((-1, 0, 1), repeat=3):
            neighbor = (cell[0] + offset[0], cell[1] + offset[1], cell[2] + offset[2])
            if neighbor not in grid:
                continue

            for satellite_index in indexes:
                satellite = bodies[satellite_index]
                if not can_fragment(satellite):
                    continue
                for primary_index in grid[neighbor]:
                    if primary_index == satellite_index:
                        continue
                    primary = bodies[primary_index]
                    if primary.mass > satellite.mass:
                        pairs[satellite_index].add(primary_index)

    return {
        satellite_index: sorted(primary_indexes)
        for satellite_index, primary_indexes in pairs.items()
    }


def _max_possible_roche_limit(bodies: list[Body]) -> float:
    density_roots = [body.density ** (1.0 / 3.0) for body in bodies]
    min_satellite_density_root = min(density_roots)
    max_primary_term = max(
        body.radius * body.density ** (1.0 / 3.0)
        for body in bodies
    )
    return 2.9 * max_primary_term / min_satellite_density_root


def _cell_key(body: Body, cell_size: float) -> tuple[int, int, int]:
    return (
        floor(float(body.position[0]) / cell_size),
        floor(float(body.position[1]) / cell_size),
        floor(float(body.position[2]) / cell_size),
    )
