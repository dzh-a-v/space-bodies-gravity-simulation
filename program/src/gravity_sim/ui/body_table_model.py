"""Qt table model for simulation bodies."""

from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from gravity_sim.core.body import Body


class BodyTableModel(QAbstractTableModel):
    HEADERS = (
        "Name",
        "Mass, kg",
        "Radius, m",
        "X, m",
        "Y, m",
        "Z, m",
        "Vx, m/s",
        "Vy, m/s",
        "Vz, m/s",
        "Ax, m/s^2",
        "Ay, m/s^2",
        "Az, m/s^2",
    )

    def __init__(self, bodies: list[Body] | None = None) -> None:
        super().__init__()
        self._bodies = bodies or []

    def set_bodies(self, bodies: list[Body]) -> None:
        self.beginResetModel()
        self._bodies = bodies
        self.endResetModel()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._bodies)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self.HEADERS)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> str | None:
        if not index.isValid() or role != Qt.DisplayRole:
            return None

        body = self._bodies[index.row()]
        values = (
            body.name,
            body.mass,
            body.radius,
            body.position[0],
            body.position[1],
            body.position[2],
            body.velocity[0],
            body.velocity[1],
            body.velocity[2],
            body.acceleration[0],
            body.acceleration[1],
            body.acceleration[2],
        )
        value = values[index.column()]
        return value if isinstance(value, str) else f"{value:.6g}"

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.DisplayRole,
    ) -> str | None:
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self.HEADERS[section]
        return str(section + 1)
