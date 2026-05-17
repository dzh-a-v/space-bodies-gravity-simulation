from gravity_sim.core.constants import MAX_MASS, MAX_RADIUS, MIN_MASS, MIN_RADIUS
from gravity_sim.core.real_bodies import REAL_BODY_PRESETS, real_body_preset_for
from gravity_sim.core.textures import RESERVED_REAL_BODY_TEXTURES


def test_real_body_presets_are_rocky_bodies_with_reserved_textures():
    assert [preset.name for preset in REAL_BODY_PRESETS] == [
        "Mercury",
        "Venus",
        "Earth",
        "Moon",
        "Mars",
    ]

    for preset in REAL_BODY_PRESETS:
        assert MIN_MASS <= preset.mass <= MAX_MASS
        assert MIN_RADIUS <= preset.radius <= MAX_RADIUS
        assert preset.texture in RESERVED_REAL_BODY_TEXTURES


def test_real_body_lookup_returns_matching_preset():
    assert real_body_preset_for("earth").name == "Earth"
    assert real_body_preset_for("moon").name == "Moon"
    assert real_body_preset_for(None) is None
    assert real_body_preset_for("custom") is None
