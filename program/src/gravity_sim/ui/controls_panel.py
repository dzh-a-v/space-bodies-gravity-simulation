"""Simulation controls panel."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from gravity_sim.core.constants import MAX_FRAGMENTS, MIN_FRAGMENTS


class ControlsPanel(QWidget):
    start_requested = Signal()
    pause_requested = Signal()
    reset_requested = Signal()
    add_body_requested = Signal()
    load_csv_requested = Signal()
    save_csv_requested = Signal()
    preset_requested = Signal(str)
    settings_changed = Signal(float, float, int)

    def __init__(self, presets: list[str]) -> None:
        super().__init__()

        self.start_button = QPushButton("Start")
        self.pause_button = QPushButton("Pause")
        self.reset_button = QPushButton("Reset")
        self.add_button = QPushButton("Add body")
        self.load_button = QPushButton("Load CSV")
        self.save_button = QPushButton("Save CSV")

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

        self.preset_combo = QComboBox()
        self.preset_combo.addItems(presets)

        run_row = QHBoxLayout()
        for button in (self.start_button, self.pause_button, self.reset_button):
            run_row.addWidget(button)

        file_row = QHBoxLayout()
        for button in (self.add_button, self.load_button, self.save_button):
            file_row.addWidget(button)

        form = QFormLayout()
        form.addRow("Time step", self.time_step)
        form.addRow("Time scale", self.time_scale)
        form.addRow("Fragments", self.fragment_count)
        form.addRow("Preset", self.preset_combo)

        layout = QVBoxLayout(self)
        layout.addLayout(run_row)
        layout.addLayout(file_row)
        layout.addLayout(form)
        layout.addStretch(1)

        self.start_button.clicked.connect(self.start_requested)
        self.pause_button.clicked.connect(self.pause_requested)
        self.reset_button.clicked.connect(self.reset_requested)
        self.add_button.clicked.connect(self.add_body_requested)
        self.load_button.clicked.connect(self.load_csv_requested)
        self.save_button.clicked.connect(self.save_csv_requested)
        self.preset_combo.activated.connect(self._emit_preset)
        self.time_step.valueChanged.connect(self._emit_settings)
        self.time_scale.valueChanged.connect(self._emit_settings)
        self.fragment_count.valueChanged.connect(self._emit_settings)

    def set_running(self, running: bool) -> None:
        self.add_button.setEnabled(not running)
        self.load_button.setEnabled(not running)
        self.preset_combo.setEnabled(not running)

    def _emit_preset(self, _index: int | None = None) -> None:
        self.preset_requested.emit(self.preset_combo.currentText())

    def _emit_settings(self) -> None:
        self.settings_changed.emit(
            self.time_step.value(),
            self.time_scale.value(),
            self.fragment_count.value(),
        )
