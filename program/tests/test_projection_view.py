from gravity_sim.core.body import Body
from gravity_sim.ui.projection_view import body_name_label_position, texture_rotation_degrees


def test_texture_rotation_completes_one_turn_per_simulated_day():
    assert texture_rotation_degrees(0.0, True) == 0.0
    assert texture_rotation_degrees(21_600.0, True) == 90.0
    assert texture_rotation_degrees(43_200.0, True) == 180.0
    assert texture_rotation_degrees(86_400.0, True) == 0.0


def test_texture_rotation_toggle_disables_rotation():
    assert texture_rotation_degrees(21_600.0, False) == 0.0


def test_body_name_label_position_is_above_projected_body():
    body = Body("A", 1e20, 1e6, [1, 2, 3], [0, 0, 0])

    assert body_name_label_position(body, 0, 1) == (1.0, 1_000_002.0)
    assert body_name_label_position(body, 0, 2) == (1.0, 1_000_003.0)
