"""Application dialogs."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QWidget,
    QVBoxLayout,
)

from gravity_sim.core.body import Body
from gravity_sim.core.real_bodies import REAL_BODY_PRESETS, real_body_preset_for
from gravity_sim.core.validation import validate_body


def show_error(parent: QWidget | None, title: str, message: str) -> None:
    QMessageBox.critical(parent, title, message)


class BodyDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Create body")

        self.preset_combo = QComboBox()
        self.preset_combo.addItem("Custom object", None)
        for preset in REAL_BODY_PRESETS:
            self.preset_combo.addItem(preset.name, preset.id)

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
        form.addRow("preset", self.preset_combo)
        for name, field in self.fields.items():
            form.addRow(name, field)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

        self.preset_combo.currentIndexChanged.connect(self._apply_preset_choice)

    def body(self) -> Body:
        values = {name: field.text().strip() for name, field in self.fields.items()}
        preset = real_body_preset_for(self.preset_combo.currentData())
        if preset is not None:
            values["name"] = preset.name
            values["mass"] = str(preset.mass)
            values["radius"] = str(preset.radius)

        body = Body(
            name=values["name"],
            mass=float(values["mass"]),
            radius=float(values["radius"]),
            position=[float(values["x"]), float(values["y"]), float(values["z"])],
            velocity=[float(values["vx"]), float(values["vy"]), float(values["vz"])],
            acceleration=[float(values["ax"]), float(values["ay"]), float(values["az"])],
            texture=preset.texture if preset is not None else None,
            real_body_id=preset.id if preset is not None else None,
        )
        validate_body(body)
        return body

    def _apply_preset_choice(self) -> None:
        preset = real_body_preset_for(self.preset_combo.currentData())
        preset_selected = preset is not None

        for field_name in ("name", "mass", "radius"):
            self.fields[field_name].setReadOnly(preset_selected)

        if preset is None:
            return

        self.fields["name"].setText(preset.name)
        self.fields["mass"].setText(f"{preset.mass:.8g}")
        self.fields["radius"].setText(f"{preset.radius:.8g}")
