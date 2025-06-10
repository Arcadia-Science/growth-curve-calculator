import pytest

from growth_curve_calculator import Well
from growth_curve_calculator.microplate import PlateType


def test_create_wells_for_96_well_plate():
    _ = Well("A", 1, PlateType.PLATE_96)
    _ = Well("H", 12, PlateType.PLATE_96)
    _ = Well.from_string("B07", PlateType.PLATE_96)

    with pytest.raises(ValueError):
        _ = Well("I", 3, PlateType.PLATE_96)
    with pytest.raises(ValueError):
        _ = Well("A", 13, PlateType.PLATE_96)
    with pytest.raises(ValueError):
        _ = Well.from_string("Q3", PlateType.PLATE_96)


def test_create_wells_for_384_well_plate():
    _ = Well("A", 1, PlateType.PLATE_384)
    _ = Well("P", 24, PlateType.PLATE_384)
    _ = Well.from_string("J22", PlateType.PLATE_384)

    with pytest.raises(ValueError):
        _ = Well("Q", 3, PlateType.PLATE_384)
    with pytest.raises(ValueError):
        _ = Well("A", 25, PlateType.PLATE_384)
    with pytest.raises(ValueError):
        _ = Well.from_string("T90", PlateType.PLATE_384)


def test_well_string_formatting():
    assert str(Well("A", 1, PlateType.PLATE_96)) == "A01"
    assert str(Well("D", 11, PlateType.PLATE_96)) == "D11"
    assert str(Well.from_string("A1", PlateType.PLATE_96)) == "A01"
    assert str(Well.from_string("D11", PlateType.PLATE_96)) == "D11"


def test_create_invalid_wells():
    with pytest.raises(ValueError):
        _ = Well("ABC", 1)
    with pytest.raises(ValueError):
        _ = Well(None, 1)  # type: ignore
    with pytest.raises(ValueError):
        _ = Well("A", None)  # type: ignore
