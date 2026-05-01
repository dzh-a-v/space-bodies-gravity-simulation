"""Main application window."""

from __future__ import annotations

import random

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QMainWindow,
    QTableView,
    QWidget,
)

from gravity_sim.core.validation import ValidationError, validate_bodies
from gravity_sim.io.csv_loader import CsvScenarioError, load_bodies_from_csv
from gravity_sim.io.csv_saver import save_bodies_to_csv
from gravity_sim.io.presets import list_presets, load_preset
from gravity_sim.physics.engine import create_default_engine

from .body_table_model import BodyTableModel
from .controls_panel import ControlsPanel
from .dialogs import BodyDialog, show_error
from .projection_view import ProjectionView


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Gravity Simulator")

        self.engine = create_default_engine()
        self.engine.rng = random.Random(0)
        self.running = False

        presets = list_presets()
        self.controls = ControlsPanel(presets)
        self.table_model = BodyTableModel(self.engine.state.bodies)
        self.table = QTableView()
        self.table.setModel(self.table_model)
        self.table.horizontalHeader().setStretchLastSection(True)

        self.projections = {
            plane: ProjectionView(plane)
            for plane in ("XY", "XZ", "YZ")
        }

        top = QHBoxLayout()
        top.addWidget(self.table, stretch=3)
        top.addWidget(self.controls, stretch=1)

        bottom = QGridLayout()
        bottom.addWidget(self.projections["XY"], 0, 0)
        bottom.addWidget(self.projections["XZ"], 0, 1)
        bottom.addWidget(self.projections["YZ"], 0, 2)

        root_layout = QGridLayout()
        root_layout.addLayout(top, 0, 0)
        root_layout.addLayout(bottom, 1, 0)
        root_layout.setRowStretch(0, 1)
        root_layout.setRowStretch(1, 2)

        root = QWidget()
        root.setLayout(root_layout)
        self.setCentralWidget(root)

        self.timer = QTimer(self)
        self.timer.setInterval(33)
        self.timer.timeout.connect(self._tick)

        self.controls.start_requested.connect(self._start)
        self.controls.pause_requested.connect(self._pause)
        self.controls.reset_requested.connect(self._reset)
        self.controls.add_body_requested.connect(self._add_body)
        self.controls.load_csv_requested.connect(self._load_csv)
        self.controls.save_csv_requested.connect(self._save_csv)
        self.controls.preset_requested.connect(self._load_preset)
        self.controls.settings_changed.connect(self._apply_settings)

        if presets:
            self._load_preset(presets[0])
        self._refresh()

    def _apply_settings(self, time_step: float, time_scale: float, fragment_count: int) -> None:
        self.engine.state.settings.time_step = time_step
        self.engine.state.settings.time_scale = time_scale
        self.engine.state.settings.fragment_count = fragment_count

    def _start(self) -> None:
        self.running = True
        self.controls.set_running(True)
        self.timer.start()

    def _pause(self) -> None:
        self.running = False
        self.controls.set_running(False)
        self.timer.stop()

    def _reset(self) -> None:
        self.running = False
        self.timer.stop()
        self.controls.set_running(False)
        self.engine.reset()
        self._refresh()

    def _tick(self) -> None:
        try:
            self.engine.step()
        except (ValidationError, ValueError) as exc:
            self._pause()
            show_error(self, "Simulation error", str(exc))
        self._refresh()

    def _refresh(self) -> None:
        bodies = self.engine.state.bodies
        self.controls.set_elapsed_time(self.engine.state.time_seconds)
        self.table_model.set_bodies(bodies)
        for projection in self.projections.values():
            projection.set_bodies(bodies)

    def _add_body(self) -> None:
        if self.running:
            return
        dialog = BodyDialog(self)
        if dialog.exec() != BodyDialog.Accepted:
            return

        try:
            bodies = [body.copy() for body in self.engine.state.bodies]
            bodies.append(dialog.body())
            validate_bodies(bodies)
            self.engine.set_bodies(bodies)
            self._refresh()
        except (ValueError, ValidationError) as exc:
            show_error(self, "Body error", str(exc))

    def _load_csv(self) -> None:
        if self.running:
            return
        path, _ = QFileDialog.getOpenFileName(self, "Load scenario", "", "CSV files (*.csv)")
        if not path:
            return
        try:
            self.engine.set_bodies(load_bodies_from_csv(path))
            self._refresh()
        except (CsvScenarioError, OSError) as exc:
            show_error(self, "CSV error", str(exc))

    def _save_csv(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Save scenario", "", "CSV files (*.csv)")
        if not path:
            return
        try:
            save_bodies_to_csv(self.engine.state.bodies, path)
        except (ValidationError, OSError) as exc:
            show_error(self, "CSV error", str(exc))

    def _load_preset(self, name: str) -> None:
        if self.running:
            return
        try:
            self.engine.set_bodies(load_preset(name))
            self._refresh()
        except (CsvScenarioError, OSError) as exc:
            show_error(self, "Preset error", str(exc))
