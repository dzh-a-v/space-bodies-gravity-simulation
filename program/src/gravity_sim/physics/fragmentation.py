"""Fragment creation and merge helpers."""

from __future__ import annotations

from math import cos, pi, sin, sqrt

from gravity_sim.core.body import Body
from gravity_sim.core.colors import WHITE
from gravity_sim.core.constants import MIN_FRAGMENTABLE_MASS, MIN_FRAGMENTS, MIN_RADIUS
from gravity_sim.core.validation import validate_fragment_count
from gravity_sim.core.vector import vector3

# Golden-angle increment for the Fibonacci sphere/ball lattice.
_GOLDEN_ANGLE = pi * (3.0 - sqrt(5.0))


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

    # Place fragment centres on a 3D Fibonacci ball-lattice. Each centre's
    # direction comes from a Fibonacci sphere (uniform on S²) and its radial
    # distance from origin grows as ((i+0.5)/N)^(1/3), which fills a ball
    # uniformly by volume. The lattice itself is unit-scaled here; we scale
    # to the parent's radius below.
    offsets: list = []
    for index in range(actual_count):
        if actual_count == 1:
            offsets.append(vector3([0.0, 0.0, 0.0]))
            continue
        cos_theta = 1.0 - 2.0 * (index + 0.5) / actual_count
        sin_theta = sqrt(max(0.0, 1.0 - cos_theta * cos_theta))
        phi = _GOLDEN_ANGLE * index
        direction = vector3([sin_theta * cos(phi), sin_theta * sin(phi), cos_theta])
        radial = ((index + 0.5) / actual_count) ** (1.0 / 3.0)
        offsets.append(direction * radial)

    # The cloud sits inside the parent's original radius — fragments occupy
    # the same region the parent did, with gaps. We scale the unit lattice so
    # that the outermost centre lies inside the parent (with a small inset so
    # fragments don't immediately leak past the parent boundary).
    OUTER_INSET = 0.95  # outermost centre at 0.95 · R_parent from the centre
    max_unit_radius = max(
        float(((off) ** 2).sum() ** 0.5) for off in offsets
    ) if actual_count > 1 else 1.0
    cloud_scale = (parent.radius * OUTER_INSET) / max_unit_radius if max_unit_radius > 0 else 0.0

    # Find the closest pair of scaled centres so we can choose a fragment
    # radius small enough to leave a comfortable surface gap between every
    # pair. Mass per fragment is fixed (= parent.mass / N); we drop strict
    # volume conservation and let fragments be denser than the parent so they
    # are spatially well-separated and don't immediately re-merge after spawn.
    min_centre_distance = float("inf")
    for i in range(actual_count):
        for j in range(i + 1, actual_count):
            distance_ij = float(
                (((offsets[i] - offsets[j]) * cloud_scale) ** 2).sum() ** 0.5
            )
            if distance_ij < min_centre_distance:
                min_centre_distance = distance_ij

    # Fragment radius rule: each fragment occupies at most a quarter of the
    # gap to its nearest neighbour, i.e. centres are 4·r_frag apart, which
    # leaves a surface gap of 2·r_frag (a full fragment diameter of empty
    # space) between the closest pair. This is well clear of the collision
    # resolver's `distance ≤ r_a + r_b` test, so fragments do not merge on
    # the next few simulation steps.
    if actual_count <= 1 or min_centre_distance == float("inf"):
        # Single fragment: keep the volume-preserving radius (purely cosmetic).
        fragment_radius = parent.radius
    else:
        fragment_radius = min_centre_distance / 4.0

    # Never shrink below MIN_RADIUS (validation lower bound). If the parent
    # is so small that this clamp would create overlapping fragments, we
    # accept the overlap rather than violate the validator — this only
    # happens for parents near MIN_RADIUS, which can barely fragment anyway.
    fragment_radius = max(fragment_radius, MIN_RADIUS)

    fragments: list[Body] = []
    for index in range(actual_count):
        offset = offsets[index] * cloud_scale
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
