"""Rigid-body collision detection and resolution."""

from __future__ import annotations

import random
from dataclasses import dataclass
from math import sqrt

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
