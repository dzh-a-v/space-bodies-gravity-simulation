"""Newtonian gravity solvers."""

from __future__ import annotations

from typing import Protocol

import numpy as np

from gravity_sim.core.body import Body
from gravity_sim.core.constants import GRAVITATIONAL_CONSTANT
from gravity_sim.core.vector import Vector3, vector3

FRAGMENT_SELF_GRAVITY_SCALE = 0.1


class GravitySolver(Protocol):
    def compute_accelerations(self, bodies: list[Body]) -> list[Vector3]:
        """Return acceleration vectors for every body."""


class DirectGravitySolver:
    """Exact pairwise O(n^2) Newtonian gravity solver."""

    def compute_accelerations(self, bodies: list[Body]) -> list[Vector3]:
        accelerations = [vector3() for _ in bodies]

        for left_index in range(len(bodies)):
            left = bodies[left_index]
            for right_index in range(left_index + 1, len(bodies)):
                right = bodies[right_index]
                delta = right.position - left.position
                distance_squared = float(np.dot(delta, delta))
                if distance_squared == 0.0:
                    continue

                interaction_scale = _interaction_scale(left, right)
                distance_cubed = distance_squared * float(np.sqrt(distance_squared))
                accelerations[left_index] += (
                    interaction_scale
                    * GRAVITATIONAL_CONSTANT
                    * right.mass
                    * delta
                    / distance_cubed
                )
                accelerations[right_index] -= (
                    interaction_scale
                    * GRAVITATIONAL_CONSTANT
                    * left.mass
                    * delta
                    / distance_cubed
                )

        return accelerations


def _interaction_scale(left: Body, right: Body) -> float:
    if (
        left.is_fragment
        and right.is_fragment
        and left.fragment_origin is not None
        and left.fragment_origin == right.fragment_origin
    ):
        return FRAGMENT_SELF_GRAVITY_SCALE
    return 1.0
