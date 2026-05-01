"""Rigid-body collision detection and resolution."""

from __future__ import annotations

import random
from collections import defaultdict
from dataclasses import dataclass
from itertools import product
from math import floor, sqrt

from gravity_sim.core.body import Body
from gravity_sim.core.constants import GRAVITATIONAL_CONSTANT
from gravity_sim.core.system_state import SimulationSettings
from gravity_sim.core.vector import distance, norm

from .fragmentation import create_fragments, merge_bodies


@dataclass(frozen=True, slots=True)
class Collision:
    left_index: int
    right_index: int


def bodies_touch(left: Body, right: Body) -> bool:
    return distance(left.position, right.position) <= left.radius + right.radius


def relative_speed(left: Body, right: Body) -> float:
    return norm(left.velocity - right.velocity)


def escape_velocity(body: Body) -> float:
    return sqrt(2.0 * GRAVITATIONAL_CONSTANT * body.mass / body.radius)


def choose_collision_outcome(
    left: Body,
    right: Body,
    rng: random.Random | None = None,
) -> str:
    rng = rng or random.Random()
    smaller = left if left.mass <= right.mass else right
    larger = right if smaller is left else left
    ratio = smaller.mass / larger.mass

    if ratio < 1.0 / 100.0:
        return "merge"

    if ratio < 1.0 / 10.0:
        fragmentation_probability = min(1.0, ratio / 0.1)
        return "fragment" if rng.random() < fragmentation_probability else "merge"

    return "fragment" if relative_speed(left, right) > escape_velocity(smaller) else "merge"


def resolve_collisions(
    bodies: list[Body],
    settings: SimulationSettings,
    rng: random.Random | None = None,
) -> list[Body]:
    """Resolve first-order pair collisions and return a new body list."""

    rng = rng or random.Random()
    consumed: set[int] = set()
    additions: list[Body] = []

    for left_index, right_index in candidate_collision_pairs(bodies):
        if left_index in consumed or right_index in consumed:
            continue

        left = bodies[left_index]
        right = bodies[right_index]
        if not bodies_touch(left, right):
            continue

        consumed.update({left_index, right_index})
        used_names = {body.name for index, body in enumerate(bodies) if index not in consumed}
        used_names.update(body.name for body in additions)
        outcome = choose_collision_outcome(left, right, rng)

        if outcome == "merge":
            additions.append(merge_bodies(left, right, used_names))
            continue

        existing_after_removal = len(bodies) - len(consumed) + len(additions)
        available_slots = max(0, settings.max_objects - existing_after_removal)
        produced: list[Body] = []

        for parent in (left, right):
            if available_slots <= 0:
                break
            fragments = create_fragments(
                parent,
                settings.fragment_count,
                used_names,
                available_slots=available_slots,
            )
            produced.extend(fragments)
            available_slots -= len(fragments)

        if produced:
            additions.extend(produced)
        else:
            additions.append(merge_bodies(left, right, used_names))

    output = [body for index, body in enumerate(bodies) if index not in consumed]
    output.extend(additions)
    return output


def candidate_collision_pairs(bodies: list[Body]) -> list[tuple[int, int]]:
    """Return exact collision candidates using a conservative spatial hash."""

    if len(bodies) < 2:
        return []

    max_radius = max(body.radius for body in bodies)
    cell_size = max(1.0, max_radius * 2.0)
    grid: dict[tuple[int, int, int], list[int]] = defaultdict(list)

    for index, body in enumerate(bodies):
        grid[_cell_key(body, cell_size)].append(index)

    pairs: set[tuple[int, int]] = set()
    for cell, indexes in grid.items():
        for offset in product((-1, 0, 1), repeat=3):
            neighbor = (cell[0] + offset[0], cell[1] + offset[1], cell[2] + offset[2])
            if neighbor not in grid:
                continue
            for left_index in indexes:
                for right_index in grid[neighbor]:
                    if left_index < right_index:
                        pairs.add((left_index, right_index))

    return sorted(pairs)


def _cell_key(body: Body, cell_size: float) -> tuple[int, int, int]:
    return (
        floor(float(body.position[0]) / cell_size),
        floor(float(body.position[1]) / cell_size),
        floor(float(body.position[2]) / cell_size),
    )


def resolve_collisions_bruteforce(
    bodies: list[Body],
    settings: SimulationSettings,
    rng: random.Random | None = None,
) -> list[Body]:
    """Legacy collision resolver kept for benchmarks."""

    rng = rng or random.Random()
    consumed: set[int] = set()
    additions: list[Body] = []

    for left_index, left in enumerate(bodies):
        if left_index in consumed:
            continue

        for right_index in range(left_index + 1, len(bodies)):
            if right_index in consumed:
                continue

            right = bodies[right_index]
            if not bodies_touch(left, right):
                continue

            consumed.update({left_index, right_index})
            used_names = {body.name for index, body in enumerate(bodies) if index not in consumed}
            used_names.update(body.name for body in additions)
            outcome = choose_collision_outcome(left, right, rng)

            if outcome == "merge":
                additions.append(merge_bodies(left, right, used_names))
                break

            existing_after_removal = len(bodies) - len(consumed) + len(additions)
            available_slots = max(0, settings.max_objects - existing_after_removal)
            produced: list[Body] = []

            for parent in (left, right):
                if available_slots <= 0:
                    break
                fragments = create_fragments(
                    parent,
                    settings.fragment_count,
                    used_names,
                    available_slots=available_slots,
                )
                produced.extend(fragments)
                available_slots -= len(fragments)

            if produced:
                additions.extend(produced)
            else:
                additions.append(merge_bodies(left, right, used_names))
            break

    output = [body for index, body in enumerate(bodies) if index not in consumed]
    output.extend(additions)
    return output
