from PySide6.QtWidgets import QApplication

from gravity_sim.core.system_state import DEFAULT_TIME_SCALE, DEFAULT_TIME_STEP
from gravity_sim.ui.controls_panel import ControlsPanel


def _app():
    return QApplication.instance() or QApplication([])


def test_controls_panel_uses_numeric_time_defaults():
    _app()

    panel = ControlsPanel([])

    assert panel.time_step.value() == DEFAULT_TIME_STEP
    assert panel.time_scale.value() == DEFAULT_TIME_SCALE
    assert panel.time_scale.maximum() == 1000.0
