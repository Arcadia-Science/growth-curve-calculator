import numpy as np

from ..spectramax import parse_spectramax_xml


def test_plate_names_sample_endpoints_1(valid_endpoint_xml_filepath_1):
    known_plate_names = [
        "Chlamy",
        "Phaeo",
    ]
    microplate_data_list = parse_spectramax_xml(valid_endpoint_xml_filepath_1)
    parsed_plate_names = [plate.name for plate in microplate_data_list]
    assert known_plate_names == parsed_plate_names


def test_plate_names_kinetic_scans(valid_kinetic_xml_filepath):
    known_plate_names = [
        "Plate 1",
        "Plate 2",
        "Plate 3",
    ]
    microplate_data_list = parse_spectramax_xml(valid_kinetic_xml_filepath)
    parsed_plate_names = [plate.name for plate in microplate_data_list]
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
    microplate_data_list = parse_spectramax_xml(valid_spectrum_scan_xml_filepath)
    parsed_plate_names = [plate.name for plate in microplate_data_list]
    assert known_plate_names == parsed_plate_names


def test_absorption_endpoint_plate_data(valid_endpoint_xml_filepath_1):
    microplate_data_list = parse_spectramax_xml(valid_endpoint_xml_filepath_1)
    microplate_data = next(plate for plate in microplate_data_list if plate.name == "Chlamy")
    parsed_measurements = microplate_data.measurements  # type: ignore

    # Test that parsed excitation wavelength is correct
    known_excitation_wavelength_nm = 750
    parsed_excitation_wavelength_nm = parsed_measurements["excitation_nm"].squeeze()  # type: ignore
    np.testing.assert_allclose(parsed_excitation_wavelength_nm, known_excitation_wavelength_nm)  # type: ignore

    # Test that parsed measurement values are correct
    known_values = {
        "A05": 0.05,
        "A06": 0.04,
        "A07": 0.042,
        "A08": 1.063,
        "H05": 0.652,
        "H06": 0.672,
        "H07": 0.047,
        "H08": 0.605,
    }
    mask = parsed_measurements.apply(  # type: ignore
        lambda row: row["well_id"] in known_values, axis=1
    )
    parsed_values = parsed_measurements.loc[mask, "value"].values  # type: ignore
    np.testing.assert_allclose(parsed_values, list(known_values.values()))  # type: ignore


def test_fluorescence_endpoint_plate_data(valid_spectrum_scan_xml_filepath):
    microplate_data_list = parse_spectramax_xml(valid_spectrum_scan_xml_filepath)
    microplate_data = next(plate for plate in microplate_data_list if plate.name == "day3pla2")
    parsed_measurements = microplate_data.measurements  # type: ignore

    # Test that parsed wavelengths are correct
    known_excitation_wavelengths_nm = [485, 561]
    parsed_excitation_wavelengths_nm = parsed_measurements["excitation_nm"].unique()  # type: ignore
    np.testing.assert_allclose(known_excitation_wavelengths_nm, parsed_excitation_wavelengths_nm)

    known_emission_wavelengths_nm = [525, 670]
    parsed_emission_wavelengths_nm = parsed_measurements["emission_nm"].unique()  # type: ignore
    np.testing.assert_allclose(parsed_emission_wavelengths_nm, known_emission_wavelengths_nm)

    # Test that parsed measurement values are correct
    known_values = {
        ("A01", 485): 3322534,
        ("A02", 485): 3196558,
        ("A03", 485): 3059612,
        ("A04", 485): 15433570,
        ("A05", 485): 6815924,
        ("A12", 485): 32490,
        ("B06", 485): 2002642,
        ("C10", 485): 9961085,
        ("D06", 485): 545762,
        ("A01", 561): 16699718,
        ("A02", 561): 16667887,
        ("A03", 561): 15063722,
        ("A12", 561): 3672,
    }
    mask = parsed_measurements.apply(  # type: ignore
        lambda row: (row["well_id"], row["excitation_nm"]) in known_values, axis=1
    )
    parsed_values = parsed_measurements.loc[mask, "value"].values  # type: ignore
    np.testing.assert_allclose(parsed_values, list(known_values.values()))  # type: ignore


def test_excitation_spectrum_scan_plate_data(valid_spectrum_scan_xml_filepath):
    microplate_data_list = parse_spectramax_xml(valid_spectrum_scan_xml_filepath)
    microplate_data = next(plate for plate in microplate_data_list if plate.name == "day7pla1EX")
    parsed_measurements = microplate_data.measurements  # type: ignore

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
    np.testing.assert_allclose(parsed_values, list(known_values.values()))  # type: ignore


def test_emission_spectrum_scan_plate_data(valid_spectrum_scan_xml_filepath):
    microplate_data_list = parse_spectramax_xml(valid_spectrum_scan_xml_filepath)
    microplate_data = next(plate for plate in microplate_data_list if plate.name == "day7pla1EM")
    parsed_measurements = microplate_data.measurements  # type: ignore

    # Test that parsed emission wavelengths are correct
    known_emission_wavelengths_nm = np.arange(480, 650 + 1, 10)
    parsed_emission_wavelengths_nm = parsed_measurements["emission_nm"].unique()  # type: ignore
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
    np.testing.assert_allclose(parsed_values, list(known_values.values()))  # type: ignore


def test_absorption_kinetic_plate_data(valid_kinetic_xml_filepath):
    microplate_data_list = parse_spectramax_xml(valid_kinetic_xml_filepath)
    microplate_data = next(plate for plate in microplate_data_list if plate.name == "Plate 2")
    parsed_measurements = microplate_data.measurements  # type: ignore

    # Test that parsed time points are correct
    known_time_points_s = np.arange(0, 180 + 1, 30)
    parsed_time_points_s = parsed_measurements["time_s"].unique()  # type: ignore
    np.testing.assert_allclose(parsed_time_points_s, known_time_points_s)

    # Test that parsed measurement values are correct
    known_values = {
        ("D01", 0): 0.057,
        ("D02", 0): 0.059,
        ("D03", 0): 0.061,
        ("D04", 0): 0.064,
        ("D05", 0): 0.065,
        ("H08", 180): 0.052,
        ("H09", 180): 0.051,
        ("H10", 180): 0.053,
        ("H11", 180): 0.051,
        ("H12", 180): 0.051,
    }
    mask = parsed_measurements.apply(  # type: ignore
        lambda row: (row["well_id"], row["time_s"]) in known_values, axis=1
    )
    parsed_values = parsed_measurements.loc[mask, "value"].values  # type: ignore
    np.testing.assert_allclose(parsed_values, list(known_values.values()))  # type: ignore
