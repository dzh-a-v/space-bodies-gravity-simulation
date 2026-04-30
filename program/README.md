# Gravity Sim

Python application for simulating gravitational interaction of spherical rigid bodies.

The project follows the technical specification in `../docs/tz/tz.tex`:

- Newtonian gravity in SI units.
- Velocity Verlet integration.
- Rigid-body collisions with merge or fragmentation outcomes.
- Roche-limit fragmentation after 24 simulated hours inside the limit.
- CSV scenario loading and saving.
- GUI with three 2D projections: `XY`, `XZ`, `YZ`, plus a live object table.

## Run

```powershell
cd program
python -m pip install -e .[dev]
gravity-sim
```

## Built-In Presets

The GUI loads CSV presets from `src/gravity_sim/resources/presets/`.

- `earth_moon.csv`
- `inner_solar_system_like.csv`
- `mars_moons.csv`
- `roche_limit_demo.csv`
- `simple_collision.csv`
- `three_body_orbits.csv`

`inner_solar_system_like.csv` is intentionally not a real Sun-based Solar System: the technical specification excludes stars and caps body mass at `1e26 kg`, so it uses a central solid-body-compatible mass.

## Tests

```powershell
cd program
pytest
```
