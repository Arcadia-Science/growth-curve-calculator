"""
More info regarding these fixtures is provided in
`growth_curve_calculator/tests/example_data/README.md`
"""

from pathlib import Path

import pytest

from growth_curve_calculator.microplate import PlateType


@pytest.fixture
def test_data_directory():
    return Path(__file__).parent / "example_data"


@pytest.fixture
def valid_endpoint_xml_filepath_1(test_data_directory):
    return test_data_directory / "sample_endpoints_1.xml"


@pytest.fixture
def valid_endpoint_xml_filepath_2(test_data_directory):
    return test_data_directory / "sample_endpoints_2.xml"


@pytest.fixture
def valid_endpoint_xml_filepath_3(test_data_directory):
    return test_data_directory / "sample_endpoints_3.xml"


@pytest.fixture
def valid_spectrum_scan_xml_filepath(test_data_directory):
    return test_data_directory / "sample_spectrum_scans.xml"


@pytest.fixture
def valid_kinetic_xml_filepath(test_data_directory):
    return test_data_directory / "sample_kinetics.xml"


@pytest.fixture
def plate_96():
    return PlateType.PLATE_96


@pytest.fixture
def plate_384():
    return PlateType.PLATE_384
