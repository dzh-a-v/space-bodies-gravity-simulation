import pytest

from gravity_sim.core.body import Body
from gravity_sim.core.validation import ValidationError, validate_bodies, validate_fragment_count


def body(name="A", mass=1e20, radius=1e6):
    return Body(name, mass, radius, [0, 0, 0], [0, 0, 0], [0, 0, 0])


def test_valid_body_list_passes():
    assert validate_bodies([body("A"), body("B")])


def test_mass_range_is_enforced():
    with pytest.raises(ValidationError):
        validate_bodies([body(mass=1e10)])


def test_radius_range_is_enforced():
    with pytest.raises(ValidationError):
        validate_bodies([body(radius=10)])


def test_names_must_be_unique():
    with pytest.raises(ValidationError):
        validate_bodies([body("A"), body("A")])


def test_fragment_count_range_is_enforced():
    assert validate_fragment_count(2) == 2
    with pytest.raises(ValidationError):
        validate_fragment_count(101)
