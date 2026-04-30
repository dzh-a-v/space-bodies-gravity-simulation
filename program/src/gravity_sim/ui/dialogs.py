"""Application dialogs."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QWidget,
    QVBoxLayout,
)

from gravity_sim.core.body import Body
from gravity_sim.core.validation import validate_body


def show_error(parent: QWidget | None, title: str, message: str) -> None:
    QMessageBox.critical(parent, title, message)


class BodyDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Create body")

        self.fields = {
            "name": QLineEdit("Body"),
            "mass": QLineEdit("1e20"),
            "radius": QLineEdit("1e6"),
            "x": QLineEdit("0"),
            "y": QLineEdit("0"),
            "z": QLineEdit("0"),
            "vx": QLineEdit("0"),
            "vy": QLineEdit("0"),
            "vz": QLineEdit("0"),
            "ax": QLineEdit("0"),
            "ay": QLineEdit("0"),
            "az": QLineEdit("0"),
        }

        form = QFormLayout()
        for name, field in self.fields.items():
            form.addRow(name, field)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def body(self) -> Body:
        values = {name: field.text().strip() for name, field in self.fields.items()}
        body = Body(
            name=values["name"],
            mass=float(values["mass"]),
            radius=float(values["radius"]),
            position=[float(values["x"]), float(values["y"]), float(values["z"])],
            velocity=[float(values["vx"]), float(values["vy"]), float(values["vz"])],
            acceleration=[float(values["ax"]), float(values["ay"]), float(values["az"])],
        )
        validate_body(body)
        return body
