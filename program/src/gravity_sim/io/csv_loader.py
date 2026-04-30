"""CSV scenario loading."""

from __future__ import annotations

import csv
from pathlib import Path

from gravity_sim.core.body import Body
from gravity_sim.core.validation import ValidationError, validate_bodies

from .csv_schema import CSV_COLUMNS


class CsvScenarioError(ValueError):
    """Raised when a CSV scenario cannot be loaded."""


def _parse_float(row: dict[str, str], column: str, row_number: int) -> float:
    try:
        return float(row[column])
    except ValueError as exc:
        raise CsvScenarioError(f"Row {row_number}: column '{column}' must be numeric.") from exc


def load_bodies_from_csv(path: str | Path) -> list[Body]:
    path = Path(path)
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None:
            raise CsvScenarioError("CSV file must contain a header row.")

        missing = [column for column in CSV_COLUMNS if column not in reader.fieldnames]
        if missing:
            raise CsvScenarioError(f"CSV file is missing required columns: {', '.join(missing)}.")

        bodies: list[Body] = []
        for row_number, row in enumerate(reader, start=2):
            try:
                bodies.append(
                    Body(
                        name=row["name"],
                        mass=_parse_float(row, "mass", row_number),
                        radius=_parse_float(row, "radius", row_number),
                        position=[
                            _parse_float(row, "x", row_number),
                            _parse_float(row, "y", row_number),
                            _parse_float(row, "z", row_number),
                        ],
                        velocity=[
                            _parse_float(row, "vx", row_number),
                            _parse_float(row, "vy", row_number),
                            _parse_float(row, "vz", row_number),
                        ],
                        acceleration=[
                            _parse_float(row, "ax", row_number),
                            _parse_float(row, "ay", row_number),
                            _parse_float(row, "az", row_number),
                        ],
                    )
                )
            except KeyError as exc:
                raise CsvScenarioError(f"Row {row_number}: missing value for {exc}.") from exc
            except ValueError as exc:
                raise CsvScenarioError(f"Row {row_number}: {exc}") from exc

    try:
        return validate_bodies(bodies)
    except ValidationError as exc:
        raise CsvScenarioError(str(exc)) from exc
