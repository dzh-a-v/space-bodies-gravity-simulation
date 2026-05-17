from gravity_sim.core.system_state import SimulationSettings, SystemState


def test_system_state_copy_preserves_artificial_coefficients_toggle():
    state = SystemState(
        settings=SimulationSettings(artificial_coefficients_enabled=False)
    )

    copied = state.copy()

    assert not copied.settings.artificial_coefficients_enabled
