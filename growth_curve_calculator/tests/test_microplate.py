import pytest

from growth_curve_calculator import Well


def test_create_wells_for_96_well_plate(plate_96):
    _ = Well("A", 1, plate_96)
    _ = Well("H", 12, plate_96)
    _ = Well.from_string("B07", plate_96)

    with pytest.raises(ValueError):
        _ = Well("I", 3, plate_96)
    with pytest.raises(ValueError):
        _ = Well("A", 13, plate_96)
    with pytest.raises(ValueError):
        _ = Well.from_string("Q3", plate_96)


def test_create_wells_for_384_well_plate(plate_384):
    _ = Well("A", 1, plate_384)
    _ = Well("P", 24, plate_384)
    _ = Well.from_string("J22", plate_384)

    with pytest.raises(ValueError):
        _ = Well("Q", 3, plate_384)
    with pytest.raises(ValueError):
        _ = Well("A", 25, plate_384)
    with pytest.raises(ValueError):
        _ = Well.from_string("T90", plate_384)


def test_well_string_formatting(plate_96):
    assert str(Well("A", 1, plate_96)) == "A01"
    assert str(Well("D", 11, plate_96)) == "D11"
    assert str(Well.from_string("A1", plate_96)) == "A01"
    assert str(Well.from_string("D11", plate_96)) == "D11"


def test_create_invalid_wells():
    with pytest.raises(ValueError):
        _ = Well("ABC", 1)
    with pytest.raises(ValueError):
        _ = Well(None, 1)  # type: ignore
    with pytest.raises(ValueError):
        _ = Well("A", None)  # type: ignore
