"""Simulation controls panel."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from gravity_sim.core.constants import (
    FRAGMENT_OBJECT_LIMIT,
    MAX_FRAGMENTS,
    MAX_OBJECTS,
    MIN_FRAGMENTS,
)


class ControlsPanel(QWidget):
    start_requested = Signal()
    pause_requested = Signal()
    reset_requested = Signal()
    add_body_requested = Signal()
    load_csv_requested = Signal()
    save_csv_requested = Signal()
    preset_requested = Signal(str)
    settings_changed = Signal(float, float, int, int)
    settings_error = Signal(str)
    texture_rotation_toggled = Signal(bool)
    artificial_coefficients_toggled = Signal(bool)

    def __init__(self, presets: list[str]) -> None:
        super().__init__()

        self.start_button = QPushButton("Start")
        self.pause_button = QPushButton("Pause")
        self.reset_button = QPushButton("Reset")
        self.add_button = QPushButton("Add body")
        self.load_button = QPushButton("Load CSV")
        self.save_button = QPushButton("Save CSV")
        self.texture_rotation_button = QPushButton("Rotation: On")
        self.texture_rotation_button.setCheckable(True)
        self.texture_rotation_button.setChecked(True)
        self.artificial_coefficients_button = QPushButton("Artificial coefficients: On")
        self.artificial_coefficients_button.setCheckable(True)
        self.artificial_coefficients_button.setChecked(True)
        self.elapsed_time = QLabel("Elapsed: 0 s")

        self.time_step = QDoubleSpinBox()
        self.time_step.setRange(0.001, 1.0e9)
        self.time_step.setDecimals(3)
        self.time_step.setValue(60.0)
        self.time_step.setSuffix(" s")

        self.time_scale = QDoubleSpinBox()
        self.time_scale.setRange(0.001, 1.0e6)
        self.time_scale.setDecimals(3)
        self.time_scale.setValue(1.0)

        self.fragment_count = QSpinBox()
        self.fragment_count.setRange(MIN_FRAGMENTS, MAX_FRAGMENTS)
        self.fragment_count.setValue(8)

        self.max_objects = QSpinBox()
        self.max_objects.setRange(0, MAX_OBJECTS)
        self.max_objects.setSingleStep(1000)
        self.max_objects.setValue(FRAGMENT_OBJECT_LIMIT)
        self.max_objects.setKeyboardTracking(False)
        self._last_valid_max_objects = FRAGMENT_OBJECT_LIMIT

        self.preset_combo = QComboBox()
        self.preset_combo.addItems(presets)

        run_row = QHBoxLayout()
        for button in (self.start_button, self.pause_button, self.reset_button):
            run_row.addWidget(button)

        file_row = QHBoxLayout()
        for button in (self.add_button, self.load_button, self.save_button):
            file_row.addWidget(button)

        form = QFormLayout()
        form.addRow("Elapsed", self.elapsed_time)
        form.addRow("Time step", self.time_step)
        form.addRow("Time scale", self.time_scale)
        form.addRow("Fragments", self.fragment_count)
        form.addRow("Max objects", self.max_objects)
        form.addRow("Preset", self.preset_combo)

        layout = QVBoxLayout(self)
        layout.addLayout(run_row)
        layout.addLayout(file_row)
        layout.addWidget(self.texture_rotation_button)
        layout.addWidget(self.artificial_coefficients_button)
        layout.addLayout(form)
        layout.addStretch(1)

        self.start_button.clicked.connect(self.start_requested)
        self.pause_button.clicked.connect(self.pause_requested)
        self.reset_button.clicked.connect(self.reset_requested)
        self.add_button.clicked.connect(self.add_body_requested)
        self.load_button.clicked.connect(self.load_csv_requested)
        self.save_button.clicked.connect(self.save_csv_requested)
        self.texture_rotation_button.toggled.connect(self._emit_texture_rotation_toggled)
        self.artificial_coefficients_button.toggled.connect(
            self._emit_artificial_coefficients_toggled
        )
        self.preset_combo.activated.connect(self._emit_preset)
        self.time_step.valueChanged.connect(self._emit_settings)
        self.time_scale.valueChanged.connect(self._emit_settings)
        self.fragment_count.valueChanged.connect(self._emit_settings)
        self.max_objects.valueChanged.connect(self._emit_settings)

    def set_running(self, running: bool) -> None:
        self.add_button.setEnabled(not running)
        self.load_button.setEnabled(not running)
        self.preset_combo.setEnabled(not running)

    def set_elapsed_time(self, seconds: float) -> None:
        total_seconds = max(0, int(seconds))
        days, remainder = divmod(total_seconds, 86_400)
        hours, remainder = divmod(remainder, 3_600)
        minutes, seconds = divmod(remainder, 60)
        if days:
            text = f"{days} d {hours:02}:{minutes:02}:{seconds:02}"
        else:
            text = f"{hours:02}:{minutes:02}:{seconds:02}"
        self.elapsed_time.setText(text)

    def _emit_preset(self, _index: int | None = None) -> None:
        self.preset_requested.emit(self.preset_combo.currentText())

    def _emit_texture_rotation_toggled(self, enabled: bool) -> None:
        self.texture_rotation_button.setText("Rotation: On" if enabled else "Rotation: Off")
        self.texture_rotation_toggled.emit(enabled)

    def _emit_artificial_coefficients_toggled(self, enabled: bool) -> None:
        text = "Artificial coefficients: On" if enabled else "Artificial coefficients: Off"
        self.artificial_coefficients_button.setText(text)
        self.artificial_coefficients_toggled.emit(enabled)

    def _emit_settings(self) -> None:
        max_objects = self.max_objects.value()
        if not 2 <= max_objects <= FRAGMENT_OBJECT_LIMIT:
            self.max_objects.blockSignals(True)
            self.max_objects.setValue(self._last_valid_max_objects)
            self.max_objects.blockSignals(False)
            self.settings_error.emit(
                f"Currently only the [2..{FRAGMENT_OBJECT_LIMIT}] range is supported."
            )
            return

        self._last_valid_max_objects = max_objects
        self.settings_changed.emit(
            self.time_step.value(),
            self.time_scale.value(),
            self.fragment_count.value(),
            max_objects,
        )
