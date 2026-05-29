# Gravity Sim

## Program

Gravity Sim is a desktop gravity simulator. For now, it supports only spherical rocky bodies.

The simulation includes:

* Newtonian gravity between all bodies;
* motion integration using the Verlet method;
* collision detection;
* merging of bodies after some collisions;
* fragmentation after high-energy collisions;
* Roche limit destruction after staying inside the critical zone for 24 simulated hours;
* loading and saving scenarios in CSV format;
* three orthogonal 2D projections: `XY`, `XZ`, and `YZ`;
* editable object table;
* preset scenarios for quick demonstrations.

All values are represented in SI units: kilograms, meters, seconds, meters per second, and so on.

## Technologies

The project is written in Python.

Main technologies:

* `PySide6` — desktop GUI;
* `pyqtgraph` — 2D visualization;
* `NumPy` — numerical calculations and vector operations;
* `pytest` — automated tests.

## Features

* Create and edit space bodies manually.
* Set mass, radius, position, velocity and acceleration.
* Update everything from the line above ↑ during simulation.
* Start, pause and reset the simulation.
* Load preset scenarios.
* Save and load custom scenarios using CSV files.
* Observe the system from three projections.
* Simulate collisions, merging, fragmentation and Roche limit destruction.

## Project structure

```text
core/       basic data structures, constants and validation
physics/    gravity, integrator, collisions, fragmentation and Roche limit
io/         CSV loading and saving
ui/         graphical interface and visualization
tests/      tests :P
```

## Current limitations

* Only spherical rocky bodies are supported;
* there is no full 3D rendering yet;
* the physical model is very simplified.

## License

GNU GPL v3 ([click](LICENSE)).

**TL;DR**

Do anything you want, but credit me and keep the project open-source, including your changes.
