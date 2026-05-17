все планеты должны иметь одну из этих текстур, выбор происходит случайно. осколки должны наследовать текстуру родителя
___
Готово.

Что сделал:
- добавил 5 PNG-текстур в `program/src/gravity_sim/resources/textures/`;
- добавил `texture` в `Body`;
- движок теперь случайно назначает текстуру всем телам без текстуры;
- фрагменты наследуют `texture` родителя;
- при слиянии новое тело сохраняет текстуру более массивного тела;
- `ProjectionView` теперь рисует текстурированные круги вместо одноцветных scatter-точек;
- обновил `pyproject.toml`, чтобы текстуры попадали в пакет;
- обновил `AGENTS.md`;
- добавил тесты на назначение/наследование текстур.

Проверил:

```text
python -m pytest
36 passed in 0.13s
```

Еще проверил headless-отрисовку текстуры:

```text
paint ok
```
___
___

Добавь вращение картинок на всех трех плоскостях со скоростью один полный оборот за сутки симулляции. Пусть будет кнопка, которая будет включать и выключать вращение
___
Готово. Добавил вращение текстур на всех трех проекциях `XY/XZ/YZ`.

Что изменилось:
- текстуры теперь поворачиваются визуально со скоростью `360°` за `86400` секунд симуляции;
- добавлена кнопка `Rotation: On/Off` в панель управления;
- выключение кнопки сразу останавливает визуальное вращение и ставит угол `0°`;
- вращение не влияет на физику, позиции, скорости, столкновения или фрагментацию;
- обновил `AGENTS.md`;
- добавил тесты на расчет угла вращения.

Проверил:

```text
python -m pytest
38 passed in 0.45s
```

И отдельно проверил headless-отрисовку с поворотом:

```text
rotated paint ok
```
___
___
добавь: при совмещении двух обьектов новый объект принимает белый цвет
___
Готово. При слиянии новый объект теперь получает `color = WHITE` и `texture = None`, поэтому в проекциях он реально отображается белым, а не с текстурой одного из родителей.

Обновил тест и `AGENTS.md`.

Проверка:

```text
python -m pytest
38 passed in 0.37s
```
___
___
- назови картинки по-простому (1.png, 2.png и т.д.)
- сделать так, чтобы у каждой планеты на сцене была случайная из этих картинка, причем они не должны повторяться, если это возможно (т.е. если количество планет на сцене < количества доступных текстур; количество текстур должно определяться программно, а не захардкодено)
___
Готово.

Что изменил:
- переименовал текстуры в `1.png`, `2.png`, `3.png`, `4.png`, `5.png`;
- убрал захардкоженный список текстур;
- теперь программа сама читает все `.png` из `resources/textures`;
- при назначении текстур обычным планетам повторы не используются, пока текстур хватает;
- если планет больше, чем текстур, повторы разрешаются;
- фрагменты по-прежнему наследуют текстуру родителя;
- белый объект после слияния не получает текстуру обратно при `engine.set_bodies()`.

Проверка:

```text
python -m pytest
42 passed in 0.45s
```
___
___
- forbid NaN and inf values when editing position, velocity, and acceleration in the table. They must be finite real numbers, same as when creating an object or loading CSV. Table edits must validate vectors too, not only mass and radius. If user enters invalid numbers, a window must pop and inform him about that.
  where to find:
  - program/src/gravity_sim/core/vector.py    vector3(...) already checks np.isfinite(...) for vectors
  - program/src/gravity_sim/ui/body_table_model.py    _apply_edit(...) writes body.position, body.velocity, body.acceleration directly
  - program/src/gravity_sim/core/validation.py    validate_body(...) currently checks finite only for mass and radius
  ___
Implemented.

Changed:
- [validation.py](</c:/Users/Домашний/Desktop/viber/space-bodies-gravity-simulation/program/src/gravity_sim/core/validation.py:46>) now rejects non-finite `position`, `velocity`, and `acceleration` values.
- [body_table_model.py](</c:/Users/Домашний/Desktop/viber/space-bodies-gravity-simulation/program/src/gravity_sim/ui/body_table_model.py:155>) now applies table vector edits through `vector3(...)`, so `nan`, `inf`, and `-inf` are rejected before commit.
- Added regression tests for table edits and core validation in [test_body_table_model.py](</c:/Users/Домашний/Desktop/viber/space-bodies-gravity-simulation/program/tests/test_body_table_model.py:17>) and [test_validation.py](</c:/Users/Домашний/Desktop/viber/space-bodies-gravity-simulation/program/tests/test_validation.py:26>).

The existing table error callback is already wired to `QMessageBox.critical(...)` in `MainWindow`, so invalid table input now triggers the popup window.

Verification: `pytest` passed, `59 passed in 63.90s`.
___
___
- add a button which enables / disables our coefficients for artificial changes of the bodies characteristics such as impulses upon collision etc.
  I think it can be done just by changing the coefficients if the user turns that parameter on/off, like it just won't affect anything this way
___
Implemented the toggle.

What changed:
- Added `artificial_coefficients_enabled` to `SimulationSettings`.
- Added a new UI button: `Artificial coefficients: On/Off`.
- When disabled:
  - collision fragment attraction impulses are skipped;
  - collision spread impulses are skipped;
  - Roche fragment attraction impulses are skipped;
  - same-origin fragment gravity scaling becomes neutral (`1.0` instead of reduced).
- The toggle is preserved across state copies/resets.

Key files:
- [controls_panel.py](</c:/Users/Домашний/Desktop/viber/space-bodies-gravity-simulation/program/src/gravity_sim/ui/controls_panel.py:51>)
- [main_window.py](</c:/Users/Домашний/Desktop/viber/space-bodies-gravity-simulation/program/src/gravity_sim/ui/main_window.py:120>)
- [system_state.py](</c:/Users/Домашний/Desktop/viber/space-bodies-gravity-simulation/program/src/gravity_sim/core/system_state.py:17>)
- [collisions.py](</c:/Users/Домашний/Desktop/viber/space-bodies-gravity-simulation/program/src/gravity_sim/physics/collisions.py:107>)
- [roche.py](</c:/Users/Домашний/Desktop/viber/space-bodies-gravity-simulation/program/src/gravity_sim/physics/roche.py:84>)
- [gravity.py](</c:/Users/Домашний/Desktop/viber/space-bodies-gravity-simulation/program/src/gravity_sim/physics/gravity.py:24>)

Verification: `pytest` passed, `63 passed in 0.47s`.
___
___





