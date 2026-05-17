import numpy as np

from PySide6.QtCore import QCoreApplication, Qt

from gravity_sim.core.body import Body
from gravity_sim.ui.body_table_model import BodyTableModel


def _app():
    return QCoreApplication.instance() or QCoreApplication([])


def body():
    return Body("A", 1e20, 1e6, [1, 2, 3], [4, 5, 6], [7, 8, 9])


def test_table_rejects_non_finite_vector_edits():
    _app()
    model = BodyTableModel([body()])
    errors: list[str] = []
    model.set_error_callback(errors.append)

    assert not model.setData(model.index(0, 3), "nan", Qt.EditRole)
    assert errors == ["Vector values must be finite numbers."]
    assert np.all(np.isfinite(model._bodies[0].position))
    assert model._bodies[0].position.tolist() == [1, 2, 3]

    assert not model.setData(model.index(0, 7), "inf", Qt.EditRole)
    assert errors[-1] == "Vector values must be finite numbers."
    assert np.all(np.isfinite(model._bodies[0].velocity))


def test_table_rejects_non_finite_acceleration_edits():
    _app()
    model = BodyTableModel([body()])
    errors: list[str] = []
    model.set_error_callback(errors.append)

    assert not model.setData(model.index(0, 11), "-inf", Qt.EditRole)
    assert errors == ["Vector values must be finite numbers."]
    assert model._bodies[0].acceleration.tolist() == [7, 8, 9]
