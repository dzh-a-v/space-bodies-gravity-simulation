"""2D orthogonal projection view."""

from __future__ import annotations

from importlib import resources

import pyqtgraph as pg

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPixmap
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from gravity_sim.core.body import Body

TEXTURE_PACKAGE = "gravity_sim.resources.textures"
TEXTURE_ROTATION_PERIOD_SECONDS = 86_400.0


def texture_rotation_degrees(time_seconds: float, enabled: bool) -> float:
    if not enabled:
        return 0.0
    return (time_seconds % TEXTURE_ROTATION_PERIOD_SECONDS) / TEXTURE_ROTATION_PERIOD_SECONDS * 360.0


class BodyTextureItem(pg.GraphicsObject):
    def __init__(self) -> None:
        super().__init__()
        self._spots: list[dict] = []
        self._bounds = QRectF()
        self._pixmaps: dict[str, QPixmap] = {}

    def set_bodies(
        self,
        bodies: list[Body],
        axis_x: int,
        axis_y: int,
        rotation_degrees: float,
    ) -> None:
        self.prepareGeometryChange()
        self._spots = [
            {
                "x": float(body.position[axis_x]),
                "y": float(body.position[axis_y]),
                "radius": float(body.radius),
                "texture": body.texture,
                "rotation_degrees": rotation_degrees,
                "color": body.color or (80, 170, 255),
            }
            for body in bodies
        ]
        self._bounds = self._compute_bounds()
        self.update()

    def boundingRect(self) -> QRectF:
        return self._bounds

    def paint(self, painter: QPainter, *args) -> None:
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        for spot in self._spots:
            radius = spot["radius"]
            target = QRectF(
                spot["x"] - radius,
                spot["y"] - radius,
                radius * 2.0,
                radius * 2.0,
            )
            pixmap = self._pixmap_for(spot["texture"])
            if pixmap is not None and not pixmap.isNull():
                clip_path = QPainterPath()
                clip_path.addEllipse(target)
                painter.save()
                painter.setClipPath(clip_path)
                painter.translate(target.center())
                painter.rotate(spot["rotation_degrees"])
                painter.translate(-target.center())
                painter.drawPixmap(target, pixmap, QRectF(pixmap.rect()))
                painter.restore()
                continue

            red, green, blue = spot["color"]
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(red, green, blue, 220))
            painter.drawEllipse(target)

    def _compute_bounds(self) -> QRectF:
        if not self._spots:
            return QRectF()

        min_x = min(spot["x"] - spot["radius"] for spot in self._spots)
        max_x = max(spot["x"] + spot["radius"] for spot in self._spots)
        min_y = min(spot["y"] - spot["radius"] for spot in self._spots)
        max_y = max(spot["y"] + spot["radius"] for spot in self._spots)
        return QRectF(min_x, min_y, max_x - min_x, max_y - min_y)

    def _pixmap_for(self, texture: str | None) -> QPixmap | None:
        if texture is None:
            return None
        if texture not in self._pixmaps:
            with resources.as_file(resources.files(TEXTURE_PACKAGE) / texture) as path:
                self._pixmaps[texture] = QPixmap(str(path))
        return self._pixmaps[texture]


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
        self.body_item = BodyTextureItem()
        self.plot.addItem(self.body_item)
        layout.addWidget(self.plot)

    def set_bodies(self, bodies: list[Body], rotation_degrees: float = 0.0) -> None:
        self.body_item.set_bodies(bodies, self._axis_x, self._axis_y, rotation_degrees)
