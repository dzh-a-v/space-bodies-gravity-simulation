import pytest

from gravity_sim.core.body import Body
from gravity_sim.io.csv_loader import CsvScenarioError, load_bodies_from_csv
from gravity_sim.io.csv_saver import save_bodies_to_csv
from gravity_sim.io.presets import list_presets, load_preset


def test_csv_round_trip(tmp_path):
    path = tmp_path / "scenario.csv"
    bodies = [
        Body("A", 1e20, 1e6, [1, 2, 3], [4, 5, 6], [7, 8, 9]),
        Body("B", 2e20, 2e6, [10, 20, 30], [40, 50, 60], [70, 80, 90]),
    ]

    save_bodies_to_csv(bodies, path)
    loaded = load_bodies_from_csv(path)

    assert [body.name for body in loaded] == ["A", "B"]
    assert loaded[0].position.tolist() == [1, 2, 3]
    assert loaded[1].velocity.tolist() == [40, 50, 60]


def test_csv_requires_schema_columns(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("name,mass\nA,1e20\n", encoding="utf-8")

    with pytest.raises(CsvScenarioError):
        load_bodies_from_csv(path)


def test_csv_rejects_duplicate_names(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text(
        "\n".join(
            [
                "name,mass,radius,x,y,z,vx,vy,vz,ax,ay,az",
                "A,1e20,1e6,0,0,0,0,0,0,0,0,0",
                "A,1e20,1e6,0,0,0,0,0,0,0,0,0",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(CsvScenarioError):
        load_bodies_from_csv(path)


def test_csv_rejects_non_numeric_values(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text(
        "\n".join(
            [
                "name,mass,radius,x,y,z,vx,vy,vz,ax,ay,az",
                "A,nope,1e6,0,0,0,0,0,0,0,0,0",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(CsvScenarioError):
        load_bodies_from_csv(path)


def test_all_packaged_presets_load_and_match_schema():
    presets = list_presets()

    assert "inner_solar_system_like.csv" in presets
    assert "mars_moons.csv" in presets
    assert "roche_limit_demo.csv" in presets
    assert "three_body_orbits.csv" in presets

    for preset in presets:
        load_preset(preset)
