from gravity_sim.core.system_state import (
    DEFAULT_TIME_SCALE,
    DEFAULT_TIME_STEP,
    SimulationSettings,
    SystemState,
)


def test_system_state_copy_preserves_artificial_coefficients_toggle():
    state = SystemState(
        settings=SimulationSettings(artificial_coefficients_enabled=False)
    )

    copied = state.copy()

    assert not copied.settings.artificial_coefficients_enabled


def test_simulation_settings_time_defaults():
    settings = SimulationSettings()

    assert settings.time_step == DEFAULT_TIME_STEP
    assert settings.time_scale == DEFAULT_TIME_SCALE
    assert settings.effective_step() == 100.0
