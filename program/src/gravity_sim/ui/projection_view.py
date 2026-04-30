"""2D orthogonal projection view."""

from __future__ import annotations

import numpy as np
import pyqtgraph as pg

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

from gravity_sim.core.body import Body


class ProjectionView(QWidget):
    AXES = {
        "XY": (0, 1),
        "XZ": (0, 2),
        "YZ": (1, 2),
    }

    def __init__(self, plane: str) -> None:
        super().__init__()
        self.plane = plane
        self._axis_x, self._axis_y = self.AXES[plane]

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        title = QLabel(f"Plane {plane}")
        layout.addWidget(title)

        self.plot = pg.PlotWidget()
        self.plot.setAspectLocked(True, ratio=1)
        self.plot.showGrid(x=True, y=True, alpha=0.25)
        self.plot.setLabel("bottom", plane[0], units="m")
        self.plot.setLabel("left", plane[1], units="m")
        self.scatter = pg.ScatterPlotItem(size=8, brush=pg.mkBrush(80, 170, 255, 210))
        self.plot.addItem(self.scatter)
        layout.addWidget(self.plot)

    def set_bodies(self, bodies: list[Body]) -> None:
        if not bodies:
            self.scatter.setData([], [])
            return

        x = np.array([body.position[self._axis_x] for body in bodies], dtype=float)
        y = np.array([body.position[self._axis_y] for body in bodies], dtype=float)
        sizes = np.array([max(6.0, min(24.0, body.radius / 1.0e6)) for body in bodies])
        self.scatter.setData(x=x, y=y, size=sizes)
