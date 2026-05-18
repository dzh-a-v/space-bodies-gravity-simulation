"""Fragment creation and merge helpers."""

from __future__ import annotations

import random
from math import cos, pi, sin, sqrt

from gravity_sim.core.body import Body
from gravity_sim.core.colors import WHITE
from gravity_sim.core.constants import (
    MIN_FRAGMENTABLE_MASS,
    MIN_FRAGMENTS,
    MIN_MASS,
    MIN_RADIUS,
)
from gravity_sim.core.validation import validate_fragment_count
from gravity_sim.core.vector import Vector3, norm, vector3

ATTRACTOR_IMPULSE_SPEED_FRACTION = 0.5
ATTRACTOR_IMPULSE_SECONDS = 1.0
COLLISION_SPREAD_SPEED_FRACTION = 0.25
COLLISION_SPREAD_RANDOM_FACTOR_MIN = 0.5
COLLISION_SPREAD_RANDOM_FACTOR_MAX = 2.5
COLLISION_SPREAD_IMPULSE_SECONDS = 1.0
FRAGMENT_TARGET_VOLUME_FRACTION = 0.1
FRAGMENT_SURFACE_GAP_FRACTION = 0.02
FRAGMENT_PLACEMENT_RESTARTS = 16
FRAGMENT_PLACEMENT_ATTEMPTS_PER_FRAGMENT = 160
FRAGMENT_RADIUS_SEARCH_STEPS = 8


def can_fragment(body: Body) -> bool:
    return not body.is_fragment and body.mass >= MIN_FRAGMENTABLE_MASS


def max_fragments_for_mass(body: Body) -> int:
    """Return how many valid fragments this body can produce by mass."""

    return int(body.mass // MIN_MASS)


def _random_offset_in_ball(radius: float, rng: random.Random) -> Vector3:
    if radius <= 0.0:
        return vector3()

    z = rng.uniform(-1.0, 1.0)
    theta = rng.uniform(0.0, 2.0 * pi)
    xy_radius = sqrt(max(0.0, 1.0 - z * z))
    direction = vector3([xy_radius * cos(theta), xy_radius * sin(theta), z])
    radial = rng.random() ** (1.0 / 3.0)
    return direction * radius * radial


def _squared_distance(left: Vector3, right: Vector3) -> float:
    dx = float(left[0] - right[0])
    dy = float(left[1] - right[1])
    dz = float(left[2] - right[2])
    return dx * dx + dy * dy + dz * dz


def _squared_norm(vector: Vector3) -> float:
    x = float(vector[0])
    y = float(vector[1])
    z = float(vector[2])
    return x * x + y * y + z * z


def _try_fragment_layout(
    parent_radius: float,
    count: int,
    fragment_radius: float,
    rng: random.Random,
    restart_limit: int = FRAGMENT_PLACEMENT_RESTARTS,
) -> list[Vector3] | None:
    available_radius = parent_radius - fragment_radius
    if available_radius < 0.0:
        return None

    min_distance = 2.0 * fragment_radius * (1.0 + FRAGMENT_SURFACE_GAP_FRACTION)
    if count > 1 and min_distance >= 2.0 * available_radius:
        return None

    min_distance_squared = min_distance * min_distance

    for _restart in range(restart_limit):
        offsets: list[Vector3] = []
        for _fragment_index in range(count):
            best_candidate: Vector3 | None = None
            best_score = -1.0
            for _attempt in range(FRAGMENT_PLACEMENT_ATTEMPTS_PER_FRAGMENT):
                candidate = _random_offset_in_ball(available_radius, rng)
                score = (
                    _squared_norm(candidate)
                    if not offsets
                    else min(_squared_distance(candidate, existing) for existing in offsets)
                )
                if score > best_score:
                    best_candidate = candidate
                    best_score = score

            if best_candidate is None or (
                offsets and best_score <= min_distance_squared
            ):
                break

            offsets.append(best_candidate)

        if len(offsets) == count:
            return offsets

    return None


def _find_fragment_layout(
    parent_radius: float,
    count: int,
    target_radius: float,
    rng: random.Random,
) -> tuple[float, list[Vector3]] | None:
    upper_radius = min(parent_radius, max(target_radius, MIN_RADIUS))
    if count > 1:
        pair_limit = parent_radius / (2.0 + FRAGMENT_SURFACE_GAP_FRACTION)
        upper_radius = min(upper_radius, pair_limit * (1.0 - 1e-12))
    if upper_radius < MIN_RADIUS:
        return None

    target_layout = _try_fragment_layout(parent_radius, count, upper_radius, rng)
    if target_layout is not None:
        return upper_radius, target_layout

    best_layout = _try_fragment_layout(parent_radius, count, MIN_RADIUS, rng)
    if best_layout is None:
        return None

    best_radius = float(MIN_RADIUS)
    low = float(MIN_RADIUS)
    high = float(upper_radius)
    if high <= low:
        return best_radius, best_layout

    for _step in range(FRAGMENT_RADIUS_SEARCH_STEPS):
        candidate_radius = (low + high) / 2.0
        candidate_layout = _try_fragment_layout(
            parent_radius,
            count,
            candidate_radius,
            rng,
            restart_limit=8,
        )
        if candidate_layout is None:
            high = candidate_radius
            continue

        best_radius = candidate_radius
        best_layout = candidate_layout
        low = candidate_radius

    return best_radius, best_layout


def unique_name(preferred: str, used_names: set[str]) -> str:
    if preferred not in used_names:
        used_names.add(preferred)
        return preferred

    suffix = 2
    while f"{preferred}_{suffix}" in used_names:
        suffix += 1

    name = f"{preferred}_{suffix}"
    used_names.add(name)
    return name


def create_fragments(
    parent: Body,
    fragment_count: int,
    used_names: set[str],
    available_slots: int | None = None,
    minimum: int = MIN_FRAGMENTS,
    rng: random.Random | None = None,
) -> list[Body]:
    """Create spherical fragments that conserve total mass."""

    validate_fragment_count(fragment_count, minimum=minimum)
    if not can_fragment(parent):
        return []

    mass_limited_count = max_fragments_for_mass(parent)
    if mass_limited_count < MIN_FRAGMENTS:
        return []

    actual_count = min(fragment_count, mass_limited_count)
    if available_slots is not None:
        actual_count = min(actual_count, max(0, available_slots))
    if actual_count < MIN_FRAGMENTS:
        return []

    rng = rng or random.Random()
    fragment_mass = parent.mass / actual_count

    # Search for the largest non-touching fragment spheres that fit inside the parent.
    target_radius = parent.radius * (FRAGMENT_TARGET_VOLUME_FRACTION / actual_count) ** (
        1.0 / 3.0
    )
    layout = _find_fragment_layout(parent.radius, actual_count, target_radius, rng)
    if layout is None:
        return []
    fragment_radius, offsets = layout

    fragments: list[Body] = []
    fragment_origin = parent.fragment_origin or parent.name
    for index in range(actual_count):
        offset = offsets[index]
        name = unique_name(f"{parent.name}_fragment_{index + 1}", used_names)
        fragments.append(
            Body(
                name=name,
                mass=fragment_mass,
                radius=fragment_radius,
                position=parent.position + offset,
                velocity=parent.velocity.copy(),
                acceleration=parent.acceleration.copy(),
                is_fragment=True,
                fragment_origin=fragment_origin,
                color=parent.color,
                texture=parent.texture,
            )
        )

    return fragments


def apply_attractor_impulse(
    parent: Body,
    attractor: Body,
    fragments: list[Body],
) -> None:
    """Kick every fragment toward an attractor with distance-based strength."""

    if attractor.mass < parent.mass:
        return

    relative_speed = norm(parent.velocity - attractor.velocity)
    impulse_speed = relative_speed * ATTRACTOR_IMPULSE_SPEED_FRACTION
    if impulse_speed <= 0.0:
        return

    fragment_distances: list[tuple[Body, float]] = []
    for fragment in fragments:
        fragment_to_attractor = attractor.position - fragment.position
        fragment_attractor_distance = norm(fragment_to_attractor)
        if fragment_attractor_distance == 0.0:
            continue
        fragment_distances.append((fragment, fragment_attractor_distance))

    if not fragment_distances:
        return

    nearest_distance = min(distance for _, distance in fragment_distances)
    farthest_distance = max(distance for _, distance in fragment_distances)
    distance_span = farthest_distance - nearest_distance

    for fragment, fragment_attractor_distance in fragment_distances:
        fragment_to_attractor = attractor.position - fragment.position
        strength = (
            1.0
            if distance_span == 0.0
            else (farthest_distance - fragment_attractor_distance) / distance_span
        )
        if strength <= 0.0:
            continue

        direction = fragment_to_attractor / fragment_attractor_distance
        impulse = direction * impulse_speed * strength
        fragment.velocity = fragment.velocity + impulse
        fragment.acceleration = fragment.acceleration + impulse / ATTRACTOR_IMPULSE_SECONDS


def apply_collision_spread_impulse(
    parent: Body,
    impact_partner: Body,
    fragments: list[Body],
    rng: random.Random | None = None,
) -> None:
    """Push side fragments away from the collision line."""

    rng = rng or random.Random()
    impact_axis = impact_partner.position - parent.position
    impact_axis_length = norm(impact_axis)
    if impact_axis_length == 0.0:
        return
    impact_axis = impact_axis / impact_axis_length

    spread_speed = (
        norm(parent.velocity - impact_partner.velocity)
        * COLLISION_SPREAD_SPEED_FRACTION
    )
    if spread_speed <= 0.0:
        return

    lateral_vectors: list[tuple[Body, Vector3, float]] = []
    for fragment in fragments:
        offset = fragment.position - parent.position
        projection = float((offset * impact_axis).sum())
        lateral = offset - projection * impact_axis
        lateral_distance = norm(lateral)
        lateral_vectors.append((fragment, lateral, lateral_distance))

    max_lateral_distance = max((distance for _, _, distance in lateral_vectors), default=0.0)
    if max_lateral_distance <= 0.0:
        return

    for fragment, lateral, lateral_distance in lateral_vectors:
        if lateral_distance <= 0.0:
            continue

        strength = lateral_distance / max_lateral_distance
        random_factor = rng.uniform(
            COLLISION_SPREAD_RANDOM_FACTOR_MIN,
            COLLISION_SPREAD_RANDOM_FACTOR_MAX,
        )
        direction = lateral / lateral_distance
        impulse = direction * spread_speed * strength * random_factor
        fragment.velocity = fragment.velocity + impulse
        fragment.acceleration = (
            fragment.acceleration + impulse / COLLISION_SPREAD_IMPULSE_SECONDS
        )


def merge_bodies(left: Body, right: Body, used_names: set[str] | None = None) -> Body:
    """Merge two bodies with mass and momentum conservation."""

    total_mass = left.mass + right.mass
    position = (left.position * left.mass + right.position * right.mass) / total_mass
    velocity = (left.velocity * left.mass + right.velocity * right.mass) / total_mass
    radius = (left.radius**3 + right.radius**3) ** (1.0 / 3.0)
    primary_name = left.name if left.mass >= right.mass else right.name
    fragment_origin = (
        left.fragment_origin
        if left.fragment_origin is not None and left.fragment_origin == right.fragment_origin
        else None
    )

    name = primary_name
    if used_names is not None:
        name = unique_name(primary_name, used_names)

    return Body(
        name=name,
        mass=total_mass,
        radius=radius,
        position=position,
        velocity=velocity,
        acceleration=vector3(),
        is_fragment=left.is_fragment or right.is_fragment,
        fragment_origin=fragment_origin,
        color=WHITE,
        texture=None,
    )
