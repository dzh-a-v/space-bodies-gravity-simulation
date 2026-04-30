"""Small helpers around numpy 3D vectors."""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
from numpy.typing import NDArray

Vector3 = NDArray[np.float64]


def vector3(values: Iterable[float] | NDArray[np.float64] | None = None) -> Vector3:
    """Return values as a finite 3D float vector."""

    if values is None:
        return np.zeros(3, dtype=float)

    array = np.asarray(list(values) if not isinstance(values, np.ndarray) else values, dtype=float)
    if array.shape != (3,):
        raise ValueError("Vector must contain exactly three numeric values.")
    if not np.all(np.isfinite(array)):
        raise ValueError("Vector values must be finite numbers.")
    return array.astype(float, copy=True)


def norm(vector: Vector3) -> float:
    return float(np.linalg.norm(vector))


def distance(left: Vector3, right: Vector3) -> float:
    return norm(left - right)
