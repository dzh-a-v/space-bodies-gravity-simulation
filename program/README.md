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

## Tests

```powershell
cd program
pytest
```
