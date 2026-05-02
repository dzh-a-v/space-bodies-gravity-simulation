"""Qt table model for simulation bodies."""

from __future__ import annotations

from typing import Callable

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from gravity_sim.core.body import Body
from gravity_sim.core.validation import ValidationError, validate_bodies


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

    NAME_COLUMN = 0

    def __init__(self, bodies: list[Body] | None = None) -> None:
        super().__init__()
        self._bodies = bodies or []
        self._editable = True
        self._commit_callback: Callable[[list[Body]], None] | None = None
        self._error_callback: Callable[[str], None] | None = None

    def set_bodies(self, bodies: list[Body]) -> None:
        self.beginResetModel()
        self._bodies = bodies
        self.endResetModel()

    def set_editable(self, editable: bool) -> None:
        self._editable = editable

    def set_commit_callback(self, callback: Callable[[list[Body]], None]) -> None:
        """Callback invoked with a fresh validated list whenever an edit succeeds."""
        self._commit_callback = callback

    def set_error_callback(self, callback: Callable[[str], None]) -> None:
        """Callback invoked with a message when an edit fails validation."""
        self._error_callback = callback

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._bodies)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self.HEADERS)

    def _value_for(self, body: Body, column: int) -> str | float:
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
        return values[column]

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> str | None:
        if not index.isValid():
            return None
        if role not in (Qt.DisplayRole, Qt.EditRole):
            return None

        body = self._bodies[index.row()]
        value = self._value_for(body, index.column())
        if role == Qt.EditRole:
            return value if isinstance(value, str) else repr(float(value))
        return value if isinstance(value, str) else f"{value:.6g}"

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        base = super().flags(index)
        if not index.isValid():
            return base
        if self._editable:
            return base | Qt.ItemIsEditable
        return base

    def setData(self, index: QModelIndex, value, role: int = Qt.EditRole) -> bool:
        if role != Qt.EditRole or not index.isValid() or not self._editable:
            return False

        row = index.row()
        column = index.column()
        if row < 0 or row >= len(self._bodies):
            return False

        # Build a fresh list of body copies and apply the edit to the copy.
        new_bodies = [body.copy() for body in self._bodies]
        target = new_bodies[row]

        try:
            self._apply_edit(target, column, value)
        except (ValueError, TypeError) as exc:
            if self._error_callback is not None:
                self._error_callback(str(exc))
            return False

        try:
            validate_bodies(new_bodies)
        except ValidationError as exc:
            if self._error_callback is not None:
                self._error_callback(str(exc))
            return False

        # Commit through the engine if a callback is wired; otherwise update
        # the local list directly.
        if self._commit_callback is not None:
            self._commit_callback(new_bodies)
        else:
            self._bodies = new_bodies
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
        return True

    @staticmethod
    def _apply_edit(body: Body, column: int, value) -> None:
        if column == 0:
            text = str(value).strip()
            if not text:
                raise ValueError("Body name must not be empty.")
            body.name = text
            return

        try:
            number = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"'{value}' is not a valid number.") from exc

        if column == 1:
            body.mass = number
        elif column == 2:
            body.radius = number
        elif 3 <= column <= 5:
            body.position[column - 3] = number
        elif 6 <= column <= 8:
            body.velocity[column - 6] = number
        elif 9 <= column <= 11:
            body.acceleration[column - 9] = number
        else:
            raise ValueError(f"Unknown column {column}.")

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
