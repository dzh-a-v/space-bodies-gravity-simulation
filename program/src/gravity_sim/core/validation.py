"""Validation rules from the technical specification."""

from __future__ import annotations

import math
from collections.abc import Iterable

from .body import Body
from .constants import (
    MAX_FRAGMENTS,
    MAX_MASS,
    MAX_OBJECTS,
    MAX_RADIUS,
    MIN_FRAGMENTS,
    MIN_MASS,
    MIN_RADIUS,
)


class ValidationError(ValueError):
    """Raised when scenario data violates the technical specification."""


def _finite(value: float, field_name: str) -> None:
    if not math.isfinite(value):
        raise ValidationError(f"{field_name} must be a finite number.")


def validate_body(body: Body) -> None:
    if not body.name:
        raise ValidationError("Body name must not be empty.")

    _finite(body.mass, "mass")
    _finite(body.radius, "radius")

    if not MIN_MASS <= body.mass <= MAX_MASS:
        raise ValidationError(f"Body '{body.name}' mass must be in [{MIN_MASS}, {MAX_MASS}].")
    if not MIN_RADIUS <= body.radius <= MAX_RADIUS:
        raise ValidationError(f"Body '{body.name}' radius must be in [{MIN_RADIUS}, {MAX_RADIUS}].")


def validate_bodies(bodies: Iterable[Body]) -> list[Body]:
    body_list = list(bodies)
    if len(body_list) > MAX_OBJECTS:
        raise ValidationError(f"Scenario contains more than {MAX_OBJECTS} bodies.")

    seen: set[str] = set()
    for body in body_list:
        validate_body(body)
        if body.name in seen:
            raise ValidationError(f"Body names must be unique: '{body.name}'.")
        seen.add(body.name)
    return body_list


def validate_fragment_count(count: int, minimum: int = MIN_FRAGMENTS) -> int:
    if not isinstance(count, int):
        raise ValidationError("Fragment count must be an integer.")
    if not minimum <= count <= MAX_FRAGMENTS:
        raise ValidationError(f"Fragment count must be in [{minimum}, {MAX_FRAGMENTS}].")
    return count
