# AI Copilot Orientation

**Read this before opening source files.** It captures what would otherwise cost dozens of file reads. Skim sections in order; only `Read` a file when this doc points you to a specific question that the doc cannot answer.

---

## 1. Project at a glance

- **What it is:** Newtonian gravity simulator for spherical rigid bodies. Python + PySide6 GUI + pyqtgraph 2D projections. SI units throughout. Single-process, single-thread.
- **Spec source of truth:** `docs/tz/tz.tex` (Russian; spec defines validation ranges and physics rules). The spec, not common sense, governs constants — if a value looks weird (e.g. `MAX_MASS = 1e26` excludes real Jupiter), it's the spec.
- **House rule (`instructions.md`):** the user does not edit code. Every change is performed by an AI assistant. Treat user requests as authoritative implementation tasks.
- **Prompts log (`README.md` at repo root):** all prompts and answers are logged in `docs/prompts/prompts.md` with `___` separators. Don't add to it yourself unless asked — but be aware it exists and may already contain context for the current task.
- **Run / test:**
  ```powershell
  cd program
  pip install -e .[dev]   # one-time
  gravity-sim             # GUI
  pytest                  # 24 tests, addopts=-q via pyproject.toml
  ```
- **Working dir convention:** the user's terminal is usually at `C:\spbpu\year2\digal\program`. Module imports always go through `gravity_sim.*` (the package root is `program/src/gravity_sim`).

---

## 2. File map (use this instead of `Glob`)

```
digal/
├── instructions.md            House rule: AI-only edits. Russian.
├── README.md                  House rule: prompts must be logged.
├── TODO.md                    Live scratchpad — read it for current focus.
├── docs/
│   ├── tz/tz.tex|pdf          Technical specification (Russian).
│   ├── plan/plan.md           Original implementation plan.
│   └── prompts/prompts.md     Append-only prompt+response log.
└── program/
    ├── pyproject.toml         Deps: numpy, PySide6, pyqtgraph. Console script: gravity-sim.
    ├── README.md              User-facing run/test instructions.
    ├── src/gravity_sim/
    │   ├── main.py            Entry point → ui.app.run_app().
    │   ├── core/
    │   │   ├── body.py        @dataclass(slots=True) Body. Has copy().
    │   │   ├── vector.py      Vector3 = numpy float64 (3,). vector3() factory validates.
    │   │   ├── colors.py      RGB tuples. WHITE reserved for merge products.
    │   │   ├── constants.py   ALL spec-mandated bounds live here. Edit with care.
    │   │   ├── system_state.py SimulationSettings + SystemState dataclasses.
    │   │   └── validation.py  validate_body / validate_bodies / validate_fragment_count.
    │   ├── physics/
    │   │   ├── engine.py      SimulationEngine — orchestrator. step() runs the pipeline.
    │   │   ├── gravity.py     DirectGravitySolver (O(n²) exact 1/r²). NO softening — see §6.
    │   │   ├── integrators.py velocity_verlet_step (mutates bodies in place).
    │   │   ├── collisions.py  bodies_touch, choose_collision_outcome, resolve_collisions.
    │   │   ├── fragmentation.py create_fragments (Fibonacci ball lattice), merge_bodies.
    │   │   └── roche.py       roche_limit, apply_roche_limit (24 h cumulative).
    │   ├── io/
    │   │   ├── csv_schema.py  CSV column tuple — single source of truth.
    │   │   ├── csv_loader.py  load_bodies_from_csv (validated, raises CsvScenarioError).
    │   │   ├── csv_saver.py   save_bodies_to_csv (validates first).
    │   │   └── presets.py     list_presets / load_preset (read from importlib.resources).
    │   ├── resources/presets/ Built-in CSV scenarios. See §5.
    │   └── ui/
    │       ├── app.py             Qt bootstrap.
    │       ├── main_window.py     Wires controls, table, projections, engine, QTimer.
    │       ├── controls_panel.py  Buttons, spinboxes, signals.
    │       ├── body_table_model.py Editable QAbstractTableModel. See §7.
    │       ├── projection_view.py 2D pyqtgraph scatter (XY/XZ/YZ). pxMode=False.
    │       └── dialogs.py         BodyDialog (Add Body), show_error.
    └── tests/                  pytest, 24 tests. See §8.
```

The compiled `_cpp_backend.cp312-win_amd64.pyd` exists alongside `__init__.py` but is not currently wired into the import path. Ignore it unless the user asks about it.

---

## 3. Domain model (memorize)

### `Body` (`core/body.py`)
Fields:
- `name: str` (stripped, unique within scenario)
- `mass: float` ∈ `[MIN_MASS, MAX_MASS] = [1e15, 1e26]` kg
- `radius: float` ∈ `[MIN_RADIUS, MAX_RADIUS] = [1e3, 2e7]` m
- `position, velocity, acceleration: Vector3` (numpy `(3,)` float64) — **mutable in place**
- `is_fragment: bool` — fragments cannot fragment again (see `can_fragment`)
- `color: tuple[int,int,int] | None` — WHITE = merge product (reserved)
- `roche_exposure_seconds: dict[str, float]` — keyed by primary name; resets when satellite leaves that primary's Roche zone

Always use `Body.copy()` when threading bodies through the engine; the dataclass holds numpy arrays and you'll get aliasing bugs otherwise. The pattern in `main_window._add_body` is canonical.

### `SimulationSettings` (`core/system_state.py`)
- `time_step: float = 60.0` (seconds, real)
- `time_scale: float = 1.0` — multiplied into `effective_step()`
- `fragment_count: int = 8` ∈ `[MIN_FRAGMENTS, MAX_FRAGMENTS] = [2, 100]`
- `max_objects: int = FRAGMENT_OBJECT_LIMIT = 10_000`

### `SystemState`
Holds `bodies: list[Body]`, `time_seconds: float`, `settings`. `copy()` deep-copies bodies and settings. `SimulationEngine.set_bodies` snapshots an `_initial_state` for `reset()`.

---

## 4. Engine pipeline (`physics/engine.py::step`)

Per tick, in order:
1. `validate_fragment_count(settings.fragment_count)` (raises early on bad UI input).
2. `dt = settings.effective_step()` if not given.
3. `velocity_verlet_step(bodies, dt, solver)` — mutates positions, velocities, accelerations.
4. `resolve_collisions(bodies, settings, rng)` — one pair per body per tick (greedy left-to-right).
5. `apply_roche_limit(bodies, settings, dt)` — accumulates exposure; fragments after `ROCHE_REQUIRED_SECONDS = 86400` cumulative inside any single primary's zone.
6. `recompute_accelerations()` — refreshes `body.acceleration` for the table view.
7. `state.time_seconds += dt`.

This ordering matters. Roche runs *after* collisions so a body merged this tick doesn't also fragment this tick.

---

## 5. Built-in presets (`resources/presets/*.csv`)

Schema: `name,mass,radius,x,y,z,vx,vy,vz,ax,ay,az` (see `io/csv_schema.py`). Loaders validate.

| Preset | Purpose |
|---|---|
| `empty.csv` | empty scenario (loader still requires header) |
| `earth_moon.csv` | real Earth-Moon, ~lunar circular orbit |
| `earth_moon_static.csv` | both stationary, used to test direct-impact collision |
| `inner_solar_system_like.csv` | Sun-less stand-in (spec excludes stars; `MAX_MASS = 1e26`) |
| `mars_moons.csv` | Mars + Phobos + Deimos |
| `simple_collision.csv` | head-on test for collision branching |
| `three_body_orbits.csv` | classic figure-8 / chaotic test |
| `roche_limit_demo.csv` | small satellite inside larger primary's Roche zone |
| `roche_close_circular.csv` | low-density icy body, deterministic Roche fragmentation |
| `roche_jupiter_grazer.csv` | gas-giant primary at the `MAX_MASS` cap |
| `roche_moon_eccentric.csv` | Moon on eccentric orbit *fully inside* Earth's Roche zone (T = 6 h, a = 1.677e7, e ≈ 0.25). Triggers fragmentation at exactly t = 86400 s. **Designed parameters — don't "fix" the orbit unless asked.** |

The Roche eccentric-Moon orbit was specifically tuned so perigee 1.25e7 m sits well above Earth radius 6.37e6 m (integrator margin) and apogee 2.10e7 m sits just inside Roche limit 2.18e7 m. Changing the velocity may break the 24 h fragmentation timing.

---

## 6. Physics gotchas (read before suggesting fixes)

- **No gravity softening.** `DirectGravitySolver` uses exact 1/r². The user explicitly rejected adding softening at `r_a + r_b` because it makes fragment clouds re-coalesce too fast. Without it, very tight fragment clusters can produce numerical kicks that fling some fragments far. Both behaviours are known. **Do not re-introduce softening without checking with the user.**
- **No fragment-fragment merge cooldown.** Tried and rejected: fragments still attract each other gravitationally, so a cooldown made them ghost through each other. Reverted in full.
- **Fragments share the parent's exact velocity** — this is intentional. Adding velocity dispersion is a candidate future change but requires user sign-off; the current contract is "only spawn positions differ from the parent".
- **Fragment layout** uses a Fibonacci ball-lattice with each fragment radius = `min_centre_distance / 4`, capped at `MIN_RADIUS`. Fragments are *denser* than the parent (mass conserved, total volume not conserved). This is by design — the volume-conserving radius caused immediate re-merging.
- **Roche fragmentation requires `is_fragment == False`** (`can_fragment`). Fragments never re-fragment, even from Roche. Roche also uses `MIN_ROCHE_FRAGMENTS = 4`, distinct from the user-controlled `fragment_count`.
- **Collision branching:**
  - mass ratio `< 1/100` → always merge
  - `1/100 ≤ ratio < 1/10` → merge probability `1 − ratio/0.1`
  - `ratio ≥ 1/10` → fragment iff `relative_speed > escape_velocity(smaller)`
  - When fragmentation outcome can't actually produce fragments (e.g. parents are already fragments), the resolver falls back to a merge.
- **Velocity Verlet** is the only integrator. Don't swap it without spec/user sign-off. It mutates bodies in place.
- **`merge_bodies` conserves momentum, not KE** (inelastic). Result is named after the more massive body and gets `color = WHITE`.
- **Projection scatter** uses `pxMode=False` so dot diameter equals true `2·radius` in meters — must match the collision condition `distance ≤ r_a + r_b`. Don't switch back to pixel mode without revisiting that match.

---

## 7. UI conventions (`ui/`)

- `MainWindow` owns the engine, a `QTimer(33ms)`, and three `ProjectionView`s. The timer drives `_tick → engine.step → _refresh`. On any `ValidationError`/`ValueError` in step, it pauses and shows a dialog.
- **Editing rule:** `BodyTableModel.set_editable(False)` while running, `True` while paused/reset. Edits go through `_commit_table_edit → engine.set_bodies → validate_bodies`. Failed edits raise into `set_error_callback` which surfaces a dialog.
- The model returns `repr(float)` for `EditRole` (full precision) and `f"{v:.6g}"` for `DisplayRole`.
- Add-body and load-CSV are gated on `not self.running`. Save-CSV is allowed at any time.
- Controls panel emits Qt Signals; main window connects them. Don't bypass the signal layer.

---

## 8. Tests (`tests/*.py` — all 24 pass at HEAD)

| Test file | What it pins down |
|---|---|
| `test_validation.py` | mass/radius range, unique names, fragment-count clamp |
| `test_gravity.py` | pairwise direction & magnitude; zero-distance returns `[0,0,0]` not NaN |
| `test_verlet.py` | constant-velocity body advances correctly with a zero-acceleration solver |
| `test_collisions.py` | small-ratio merge / equal-fast fragmentation / equal-slow merge |
| `test_fragmentation.py` | mass conservation, fragment-name prefix, `is_fragment` block, slot truncation |
| `test_roche.py` | exposure accumulates over 24 h then fragments; resets when leaving zone |
| `test_csv_io.py` | round-trip; missing columns / dup names / non-numeric all raise; presets all load |
| `test_colors.py` | unique non-white initial palette; fragments inherit parent color; merge → WHITE |

`pytest` from `program/` Just Works (config in `pyproject.toml`). When you change physics, run all tests. When you change UI, tests don't cover Qt — verify by reasoning + targeted snippets via the engine API.

---

## 9. Common task recipes (token-saving heuristics)

- **"Add a preset"** → write CSV under `program/src/gravity_sim/resources/presets/`. Verify with `load_preset(name)` (it validates). It will appear in the GUI dropdown automatically. Also confirms a 24 h Roche scenario actually triggers in `engine.step` if the preset's purpose is Roche.
- **"Change a validation bound"** → edit `core/constants.py` and check `core/validation.py`, then run tests. The spec (`docs/tz/tz.tex`) is authoritative — flag any divergence before changing.
- **"Edit a Body field in the GUI"** → see §7. Don't add new mutating paths; route through `_commit_table_edit`.
- **"Fragments behave wrong"** → §6 first. The user has a strong opinion about fragment layout, velocity dispersion, and softening, and has already rejected several plausible fixes. Ask before re-trying any of them.
- **"Make integration faster / more accurate"** → not in scope without explicit user instruction. Velocity Verlet is required by spec.

---

## 10. Things to *not* do

- **Don't** introduce gravity softening, fragment cooldowns, or fragment velocity dispersion without explicit user approval (all previously tried & reverted).
- **Don't** edit `tz.tex`, `plan.md`, or `prompts.md` proactively.
- **Don't** edit code without a user request — `instructions.md` forbids unsolicited refactors.
- **Don't** add docs files (READMEs etc.) unless explicitly asked.
- **Don't** add emojis to source/docs unless asked.
- **Don't** reach for `Glob`/`Grep` first when this doc already maps the file. Read the doc, then jump straight to the right file.

---

## 11. When this doc is wrong

Fast checks if you suspect drift:
- File list outdated → `ls program/src/gravity_sim/**/*.py`.
- Constant changed → `program/src/gravity_sim/core/constants.py` is short, just read it.
- Test count changed → `pytest --collect-only -q`.
- New preset → `ls program/src/gravity_sim/resources/presets/`.
- Behaviour was reverted/changed → `git log --oneline -20`.

If you fix the codebase, also fix this doc in the same change.
