# fix
- when the object is destructing, need to check the expected mass of the fragments: the mass of each fragment must be above ≥ 1e15 kg. If it is impossible to destruct the object into set number of fragments, the program must compute the maximum possible number of fragments so that each fragment will have mass ≥1e15. if it is impossible to destruct the object following this rule (e.g. its mass is \<2e15), it mustn't destruct.
  where to find:
  - program/src/gravity_sim/core/constants.py	MIN_MASS = 1.0e15
  - program/src/gravity_sim/core/validation.py	validate_body(...) проверяет массу обычных объектов
  - program/src/gravity_sim/physics/fragmentation.py	fragment_mass = parent.mass / actual_count
  - program/src/gravity_sim/physics/fragmentation.py	Body(..., mass=fragment_mass, ...)

- forbid creating objects which are not just rocky bodies. tell the user it's not supported yet.
  where to find:
  - program/src/gravity_sim/core/validation.py	validate_body(...) проверяет имя, массу и радиус, но не тип объекта
  - program/src/gravity_sim/resources/presets/roche_jupiter_grazer.csv	строка GasGiant,1.0e26,2.0e7,...

- forbid NaN and inf values when editing position, velocity, and acceleration in the table. They must be finite real numbers, same as when creating an object or loading CSV. Table edits must validate vectors too, not only mass and radius.
  where to find:
  - program/src/gravity_sim/core/vector.py    vector3(...) already checks np.isfinite(...) for vectors
  - program/src/gravity_sim/ui/body_table_model.py    _apply_edit(...) writes body.position, body.velocity, body.acceleration directly
  - program/src/gravity_sim/core/validation.py    validate_body(...) currently checks finite only for mass and radius

- fix Roche fragmentation when there are no available object slots left. If available_slots is 0 and no fragments can be created, the original body must not disappear from the simulation. The program must either create the allowed number of fragments or keep the body unchanged.
  where to find:
  - program/src/gravity_sim/physics/roche.py    consumed.add(satellite_index)
  - program/src/gravity_sim/physics/roche.py    available_slots calculation
  - program/src/gravity_sim/physics/roche.py    additions.extend(fragments) currently runs without checking that fragments were actually created

- add separate Roche fragment count setting in UI. Collision fragmentation must use 2..100, Roche fragmentation must use 4..100. Remove silent max(settings.fragment_count, MIN_ROCHE_FRAGMENTS) behavior and pass roche_fragment_count explicitly.
  where to find:
  - program/src/gravity_sim/core/system_state.py    SimulationSettings currently has only fragment_count
  - program/src/gravity_sim/ui/controls_panel.py    one Fragments spinbox with range 2..100
  - program/src/gravity_sim/physics/collisions.py    uses settings.fragment_count
  - program/src/gravity_sim/physics/roche.py    currently uses max(settings.fragment_count, MIN_ROCHE_FRAGMENTS)
 
- add a button which enables / disables our coefficients for artificial changes of the bodies characteristics such as impulses upon collision etc.
  I think it can be done just by changing the coefficients if the user turns that parameter on/off, like it just won't affect anything this way

# check

# feat

## later
- lock view at one object
- lock view at several objects
- lock scale when it enlarged (for some time, so that it is not constantly zooming in and out)

# notes
- Now when the Moon and the Earth are static and the step of the simulation is 1 second, they unite upon collision.
- !!!!! In collision simulation, the objects break into fragments and those fragments perfectly go to each other instead of flying to different sides.

# results
## good simulations
- [x] Earth and Moon
- [x] three objects
