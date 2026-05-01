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

The app uses the optional C++ backend when it was built successfully. If no C++
compiler is available, installation still works and the simulator falls back to
the vectorized Python backend.

## Performance

Physics runs behind a backend interface:

- `CppExactBackend`: exact Newtonian `O(n^2)` gravity and Velocity Verlet in C++.
- `PythonBackend`: exact vectorized `numpy` fallback.

Run the benchmark:

```powershell
cd program
gravity-sim-benchmark
```

Useful variants:

```powershell
gravity-sim-benchmark --counts 100,500,1000 --repeats 5
gravity-sim-benchmark --counts 500 --include-gui
```

For scenarios with tens of thousands of bodies, exact `O(n^2)` gravity will
still become expensive. The current backend interface is designed so a future
Barnes-Hut backend can be added without replacing the GUI.

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
