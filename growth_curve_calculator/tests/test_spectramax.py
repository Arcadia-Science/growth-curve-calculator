import numpy as np
import pytest

from ..spectramax import SpectraMaxXmlParser, get_microplate_data_by_name


def test_plate_names_sample_endpoints_1(valid_endpoint_xml_filepath_1):
    known_plate_names = [
        "Chlamy",
        "Phaeo",
    ]
    parser = SpectraMaxXmlParser(valid_endpoint_xml_filepath_1)
    parsed_plate_names = parser.plate_names
    assert known_plate_names == parsed_plate_names


def test_plate_names_sample_kinetics(valid_kinetic_xml_filepath):
    known_plate_names = [
        "Plate 1",
        "Plate 2",
        "Plate 3",
    ]
    parser = SpectraMaxXmlParser(valid_kinetic_xml_filepath)
    parsed_plate_names = parser.plate_names
    assert known_plate_names == parsed_plate_names


def test_plate_names_sample_spectrum_scans(valid_spectrum_scan_xml_filepath):
    known_plate_names = [
        "day 1",
        "day 2",
        "day3pla1",
        "day3pla2",
        "day4pla1",
        "day5pla1",
        "day6pla1",
        "day7pla1",
        "day7pla2",
        "day7pla1EX",
        "day7pla2EX",
        "day7pla1EM",
        "day7pla2EM",
        "day6pla2",
        "day5pla2",
        "day4pla2",
        "od600",
    ]
    parser = SpectraMaxXmlParser(valid_spectrum_scan_xml_filepath)
    parsed_plate_names = parser.plate_names
    assert known_plate_names == parsed_plate_names


@pytest.fixture
def valid_absorption_endpoint_plate_data(valid_endpoint_xml_filepath_1):
    return get_microplate_data_by_name(valid_endpoint_xml_filepath_1, "Chlamy")


@pytest.fixture
def valid_fluorescence_endpoint_plate_data(valid_spectrum_scan_xml_filepath):
    return get_microplate_data_by_name(valid_spectrum_scan_xml_filepath, "day3pla2")


@pytest.fixture
def valid_kinetic_plate_data(valid_kinetic_xml_filepath):
    return get_microplate_data_by_name(valid_kinetic_xml_filepath, "Plate 2")


@pytest.fixture
def valid_excitation_spectrum_scan_plate_data(valid_spectrum_scan_xml_filepath):
    return get_microplate_data_by_name(valid_spectrum_scan_xml_filepath, "day7pla1EX")


@pytest.fixture
def valid_emission_spectrum_scan_plate_data(valid_spectrum_scan_xml_filepath):
    return get_microplate_data_by_name(valid_spectrum_scan_xml_filepath, "day7pla1EM")


def test_absorption_endpoint_plate_data(valid_absorption_endpoint_plate_data):
    parsed_measurements = valid_absorption_endpoint_plate_data.measurements  # type: ignore

    # Test that parsed excitation wavelength is correct
    known_excitation_wavelength_nm = 750
    parsed_excitation_wavelength_nm = parsed_measurements["excitation_nm"].squeeze()  # type: ignore
    np.testing.assert_allclose(parsed_excitation_wavelength_nm, known_excitation_wavelength_nm)

    # Test that parsed measurement values are correct
    known_values = {
        "A06": 0.05,
        "H09": 0.605,
    }
    mask = parsed_measurements.apply(  # type: ignore
        lambda row: row["well_id"] in known_values, axis=1
    )
    parsed_values = parsed_measurements.loc[mask, "value"].values  # type: ignore
    np.testing.assert_allclose(parsed_values, list(known_values.values()))


def test_fluorescence_endpoint_plate_data(valid_fluorescence_endpoint_plate_data):
    parsed_measurements = valid_fluorescence_endpoint_plate_data.measurements  # type: ignore

    # Test that parsed wavelengths are correct
    known_excitation_wavelengths_nm = [485, 561]
    parsed_excitation_wavelengths_nm = parsed_measurements["excitation_nm"].unique()  # type: ignore
    np.testing.assert_allclose(known_excitation_wavelengths_nm, parsed_excitation_wavelengths_nm)

    known_emission_wavelengths_nm = [525, 670]
    parsed_emission_wavelengths_nm = parsed_measurements["emission_nm"].unique()  # type: ignore
    np.testing.assert_allclose(parsed_emission_wavelengths_nm, known_emission_wavelengths_nm)

    # Test that parsed measurement values are correct
    known_values = {
        # ("A01", 485): 3322534,
        ("A02", 485): 3322534,
        # ("D06", 485): 545762,
        # ("A01", 561): 16699718,
        ("A02", 561): 16699718,
        # ("D06", 561): 18477,
    }
    mask = parsed_measurements.apply(  # type: ignore
        lambda row: (row["well_id"], row["excitation_nm"]) in known_values, axis=1
    )
    parsed_values = parsed_measurements.loc[mask, "value"].values  # type: ignore
    np.testing.assert_allclose(parsed_values, list(known_values.values()))


def test_excitation_spectrum_scan_plate_data(valid_excitation_spectrum_scan_plate_data):
    parsed_measurements = valid_excitation_spectrum_scan_plate_data.measurements  # type: ignore

    # Test that parsed excitation wavelengths are correct
    known_excitation_wavelengths_nm = np.arange(350, 520 + 1, 10)
    parsed_excitation_wavelengths_nm = parsed_measurements["excitation_nm"].unique()  # type: ignore
    np.testing.assert_allclose(parsed_excitation_wavelengths_nm, known_excitation_wavelengths_nm)

    # Test that parsed measurement values are correct
    known_values = {
        ("A01", 350): 4416022,
        ("B01", 350): 7020090,
        ("C01", 350): 4171942,
        ("H01", 350): 6535411,
        ("A10", 520): 1596989,
        ("B06", 520): 384516,
        ("C10", 520): 1416205,
        ("H06", 520): 396659,
    }
    mask = parsed_measurements.apply(  # type: ignore
        lambda row: (row["well_id"], row["excitation_nm"]) in known_values, axis=1
    )
    parsed_values = parsed_measurements.loc[mask, "value"].values  # type: ignore
    np.testing.assert_allclose(parsed_values, list(known_values.values()))


def test_emission_spectrum_scan_plate_data(valid_emission_spectrum_scan_plate_data):
    parsed_measurements = valid_emission_spectrum_scan_plate_data.measurements  # type: ignore

    # Test that parsed emission wavelengths are correct
    known_emission_wavelengths_nm = np.arange(480, 650 + 1, 10)
    parsed_emission_wavelengths_nm = parsed_measurements["emission_nm"].unique().tolist()  # type: ignore
    np.testing.assert_allclose(parsed_emission_wavelengths_nm, known_emission_wavelengths_nm)

    # Test that parsed measurement values are correct
    known_values = {
        ("A01", 480): 6994224,
        ("B01", 480): 13572286,
        ("C01", 480): 6537449,
        ("H01", 480): 11618648,
        ("A10", 650): 3428402,
        ("B06", 650): 991546,
        ("C10", 650): 3146519,
        ("H06", 650): 988925,
    }
    mask = parsed_measurements.apply(  # type: ignore
        lambda row: (row["well_id"], row["emission_nm"]) in known_values, axis=1
    )
    parsed_values = parsed_measurements.loc[mask, "value"].values  # type: ignore
    np.testing.assert_allclose(parsed_values, list(known_values.values()))
