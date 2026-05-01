"""Fragment creation and merge helpers."""

from __future__ import annotations

from math import cos, pi, sin

from gravity_sim.core.body import Body
from gravity_sim.core.colors import WHITE
from gravity_sim.core.constants import MIN_FRAGMENTABLE_MASS, MIN_FRAGMENTS
from gravity_sim.core.validation import validate_fragment_count
from gravity_sim.core.vector import vector3


def can_fragment(body: Body) -> bool:
    return not body.is_fragment and body.mass >= MIN_FRAGMENTABLE_MASS


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
) -> list[Body]:
    """Create spherical fragments that conserve total mass."""

    validate_fragment_count(fragment_count, minimum=minimum)
    if not can_fragment(parent):
        return []

    actual_count = fragment_count
    if available_slots is not None:
        actual_count = min(actual_count, max(0, available_slots))
    if actual_count <= 0:
        return []

    fragment_mass = parent.mass / actual_count
    fragment_radius = parent.radius / actual_count ** (1.0 / 3.0)
    fragments: list[Body] = []

    for index in range(actual_count):
        angle = 2.0 * pi * index / actual_count
        layer = -0.5 if index % 2 else 0.5
        direction = vector3([cos(angle), sin(angle), layer])
        offset = direction * parent.radius * 1.05
        name = unique_name(f"{parent.name}_fragment_{index + 1}", used_names)
        fragments.append(
            Body(
                name=name,
                mass=fragment_mass,
                radius=fragment_radius,
                position=parent.position + offset,
                velocity=parent.velocity + direction,
                acceleration=parent.acceleration.copy(),
                is_fragment=True,
                color=parent.color,
            )
        )

    return fragments


def merge_bodies(left: Body, right: Body, used_names: set[str] | None = None) -> Body:
    """Merge two bodies with mass and momentum conservation."""

    total_mass = left.mass + right.mass
    position = (left.position * left.mass + right.position * right.mass) / total_mass
    velocity = (left.velocity * left.mass + right.velocity * right.mass) / total_mass
    radius = (left.radius**3 + right.radius**3) ** (1.0 / 3.0)
    primary_name = left.name if left.mass >= right.mass else right.name

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
        color=WHITE,
    )
