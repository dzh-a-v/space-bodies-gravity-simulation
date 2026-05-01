"""Command-line benchmarks for simulation hotspots."""

from __future__ import annotations

import argparse
import os
import random
from collections.abc import Callable
from time import perf_counter

import numpy as np

from gravity_sim.core.body import Body
from gravity_sim.core.colors import initial_palette
from gravity_sim.core.snapshot import bodies_to_snapshot
from gravity_sim.core.system_state import SimulationSettings
from gravity_sim.physics.backends import PythonBackend, create_best_backend
from gravity_sim.physics.collisions import resolve_collisions
from gravity_sim.physics.engine import SimulationEngine
from gravity_sim.physics.roche import apply_roche_limit


DEFAULT_COUNTS = (100, 500, 1000, 3000)


def generate_benchmark_bodies(count: int) -> list[Body]:
    """Create a deterministic, non-colliding cloud of valid bodies."""

    bodies: list[Body] = []
    colors = initial_palette(count)
    grid_width = max(1, int(np.ceil(count ** (1.0 / 3.0))))
    spacing = 2.0e7

    for index in range(count):
        x_index = index % grid_width
        y_index = (index // grid_width) % grid_width
        z_index = index // (grid_width * grid_width)
        position = [
            (x_index - grid_width / 2) * spacing,
            (y_index - grid_width / 2) * spacing,
            (z_index - grid_width / 2) * spacing,
        ]
        bodies.append(
            Body(
                name=f"Body_{index}",
                mass=1.0e18 + index * 1.0e12,
                radius=1.0e3,
                position=position,
                velocity=[0.0, 0.0, 0.0],
                color=colors[index],
            )
        )

    return bodies


def benchmark_counts(
    counts: tuple[int, ...] = DEFAULT_COUNTS,
    repeats: int = 3,
    include_gui: bool = False,
) -> list[dict[str, float | int | str]]:
    backend = create_best_backend()
    fallback = PythonBackend()
    rows: list[dict[str, float | int | str]] = []

    for count in counts:
        bodies = generate_benchmark_bodies(count)
        snapshot = bodies_to_snapshot(bodies)
        settings = SimulationSettings(fragment_count=8)
        rows.append(
            {
                "n": count,
                "backend": backend.name,
                "gravity_ms": _measure(lambda: backend.compute_accelerations(snapshot), repeats),
                "verlet_ms": _measure(lambda: backend.step(snapshot, 60.0), repeats),
                "python_gravity_ms": _measure(
                    lambda: fallback.compute_accelerations(snapshot),
                    repeats,
                ),
                "collisions_ms": _measure(
                    lambda: resolve_collisions([body.copy() for body in bodies], settings, random.Random(0)),
                    repeats,
                ),
                "roche_ms": _measure(
                    lambda: apply_roche_limit([body.copy() for body in bodies], settings, 60.0),
                    repeats,
                ),
                "gui_refresh_ms": _measure_gui_refresh(bodies, repeats) if include_gui else -1.0,
            }
        )

    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark gravity_sim physics hotspots.")
    parser.add_argument(
        "--counts",
        default=",".join(str(count) for count in DEFAULT_COUNTS),
        help="Comma-separated body counts.",
    )
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--include-gui", action="store_true")
    args = parser.parse_args()

    counts = tuple(int(item.strip()) for item in args.counts.split(",") if item.strip())
    rows = benchmark_counts(counts=counts, repeats=args.repeats, include_gui=args.include_gui)
    _print_rows(rows)
    return 0


def _measure(callback: Callable[[], object], repeats: int) -> float:
    elapsed: list[float] = []
    for _ in range(max(1, repeats)):
        started_at = perf_counter()
        callback()
        elapsed.append(perf_counter() - started_at)
    return min(elapsed) * 1000.0


def _measure_gui_refresh(bodies: list[Body], repeats: int) -> float:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    from gravity_sim.ui.main_window import MainWindow

    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window.engine = SimulationEngine()
    window.engine.set_bodies([body.copy() for body in bodies])
    result = _measure(lambda: window._refresh(force=True), repeats)
    window.close()
    app.processEvents()
    return result


def _print_rows(rows: list[dict[str, float | int | str]]) -> None:
    headers = (
        "n",
        "backend",
        "gravity_ms",
        "verlet_ms",
        "python_gravity_ms",
        "collisions_ms",
        "roche_ms",
        "gui_refresh_ms",
    )
    print(" | ".join(headers))
    print(" | ".join("-" * len(header) for header in headers))
    for row in rows:
        print(
            " | ".join(
                str(row[header]) if not isinstance(row[header], float) else f"{row[header]:.3f}"
                for header in headers
            )
        )


if __name__ == "__main__":
    raise SystemExit(main())
