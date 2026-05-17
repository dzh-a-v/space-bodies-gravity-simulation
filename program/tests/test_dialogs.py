from PySide6.QtWidgets import QApplication

from gravity_sim.ui.dialogs import BodyDialog


def _app():
    return QApplication.instance() or QApplication([])


def test_body_dialog_can_create_real_body_preset():
    _app()
    dialog = BodyDialog()
    dialog.preset_combo.setCurrentIndex(dialog.preset_combo.findData("mars"))
    dialog.fields["x"].setText("1")
    dialog.fields["vy"].setText("2")

    body = dialog.body()

    assert body.name == "Mars"
    assert body.mass == 6.4171e23
    assert body.radius == 3.3895e6
    assert body.texture == "mars.png"
    assert body.real_body_id == "mars"
    assert body.position.tolist() == [1, 0, 0]
    assert body.velocity.tolist() == [0, 2, 0]
    assert dialog.fields["name"].isReadOnly()
    assert dialog.fields["mass"].isReadOnly()
    assert dialog.fields["radius"].isReadOnly()


def test_body_dialog_custom_body_has_no_reserved_texture():
    _app()
    dialog = BodyDialog()

    body = dialog.body()

    assert body.texture is None
    assert body.real_body_id is None
