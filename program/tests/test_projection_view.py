from gravity_sim.ui.projection_view import texture_rotation_degrees


def test_texture_rotation_completes_one_turn_per_simulated_day():
    assert texture_rotation_degrees(0.0, True) == 0.0
    assert texture_rotation_degrees(21_600.0, True) == 90.0
    assert texture_rotation_degrees(43_200.0, True) == 180.0
    assert texture_rotation_degrees(86_400.0, True) == 0.0


def test_texture_rotation_toggle_disables_rotation():
    assert texture_rotation_degrees(21_600.0, False) == 0.0
