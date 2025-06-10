from __future__ import annotations
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Generator

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from bs4.element import Tag

from .microplate import MicroplateData, PlateType, Well
from .utils import forward_fill_indices, value_to_float

logger = logging.getLogger(__name__)


class SpectraMaxXmlParser:
    """An XML parser for interpreting the output of the SpectraMax iD3 microplate reader.

    Attributes:
        xml_filepath: File path to XML file.
        soup: A BeautifulSoup object representing the parsed XML file.
        datetime_format: Datetime format for `datetime.strptime`.

    See also:
        parse_spectramax_xml
    """

    def __init__(self, xml_filepath: Path | str) -> None:
        """Initialize the SpectraMaxXmlParser with a file path to an XML file.

        Args:
            xml_filepath: File path to the XML file output by the SpectraMax iD3 plate reader.
        """
        self.xml_filepath = Path(xml_filepath)
        xml_text = self.xml_filepath.read_text()
        self.soup = BeautifulSoup(xml_text, features="xml")
        self.datetime_format = "%m/%d/%Y %H:%M:%S"

    @property
    def plate_names(self) -> list[str]:
        """Get a list of all plate names in the XML file.

        Returns:
            A list of strings representing the names of all plates in the XML file.

        Example:
            >>> parser = SpectraMaxXmlParser("plate_data.xml")
            >>> parser.plate_names
            ['Plate1', 'Plate2', 'Control Plate']
        """
        xml_rows = self.soup.find_all("ss:Row", recursive=True)
        _plate_names = [
            re.sub("\n+", "\n", xml_row.text.strip().split("\n")[-1])
            for xml_row in xml_rows
            if xml_row.find("ss:Cell")
            and xml_row.find("ss:Data")
            and xml_row.find("ss:Data").text == "Plate name"
        ]
        return _plate_names

    @property
    def num_plates(self) -> int:
        return len(self.plate_names)

    def parse(self) -> list[MicroplateData]:
        """Parse the XML file and return a list of MicroplateData objects.

        This is the main entry point for parsing SpectraMax XML files. It processes the XML file
        and extracts plate measurements, converting them to MicroplateData objects containing
        structured data that can be easily analyzed.

        Returns:
            A list of MicroplateData objects representing the parsed plate measurements found in
            the XML file.
        """
        return list(self.generate_plate_measurements())

    def generate_plate_measurements(self) -> Generator[MicroplateData, None, None]:
        """Generate MicroplateData objects from the XML file.

        Yields:
            MicroplateData objects for each plate measurement in the XML file.

        Raises:
            ValueError:
                - If no plate reader data could be parsed from the XML file.
        """
        lists_of_plate_reader_xml = self._get_lists_of_plate_reader_xml()
        if not lists_of_plate_reader_xml:
            raise ValueError(
                "Unable to parse any data from the plate reader. Check contents of XML file."
            )

        for plate_reader_xml in lists_of_plate_reader_xml:
            yield self._parse_plate_reader_xml(plate_reader_xml)

    def prettify(self) -> None:
        """Prints the XML data in a more legible manner (useful for debugging)."""
        rows_of_prettified_text: list[str] = []
        for xml_row in self.soup.find_all("ss:Row"):
            xml_row_text = re.sub("\n+", "\n", xml_row.text)
            row_of_prettified_text = " | ".join(xml_row_text.strip().split("\n"))
            rows_of_prettified_text.append(row_of_prettified_text)
        prettified_text = "\n".join(rows_of_prettified_text)
        print(prettified_text)

    def _get_lists_of_plate_reader_xml(self) -> list[list[Tag | None]]:
        """Extract plate reader XML data by finding sections that start with "Plate name".

        Returns:
            A list of lists, where each inner list contains the XML tags for a single plate
            measurement.
        """
        # Simplest way to find each set of plate measurements is to find rows with "Plate name"
        xml_rows = self.soup.find_all("ss:Row", recursive=True)
        plate_name_rows = [
            xml_row
            for xml_row in xml_rows
            if xml_row.find("ss:Cell")
            and xml_row.find("ss:Data")
            and xml_row.find("ss:Data").text == "Plate name"
        ]

        lists_of_plate_reader_xml: list[list[Tag | None]] = []
        for i, row in enumerate(plate_name_rows):
            # Get the header row of each plate measurement
            header_row = row.find_previous("ss:Row")

            # Define the end of each plate measurement
            if i < len(plate_name_rows) - 1:
                # If not the last plate, end is the next plate's header
                # (really it should be the row before the next plate's header, but this row has
                # a nonzero chance of being empty and therefore hard to match -- in these cases
                # define a flag to avoid reading the last row)
                end_row = plate_name_rows[i + 1].find_previous("ss:Row")
                read_last_row = False
            else:
                # If last plate, find all rows after this and take the last one
                end_row = self.soup.find_all("ss:Row")[-1]
                read_last_row = True

            # Get the xml from an individual plate read
            plate_reader_xml = self._extract_plate_reader_xml(
                start_row=header_row,
                end_row=end_row,
                read_last_row=read_last_row,
            )
            lists_of_plate_reader_xml.append(plate_reader_xml)

        return lists_of_plate_reader_xml

    def _extract_plate_reader_xml(
        self,
        start_row: Tag,
        end_row: Tag,
        read_last_row: bool,
    ) -> list[Tag | None]:
        """Extract all XML content between `start_row` and `end_row`.

        This method collects all rows between the start and end rows (inclusive of start row),
        and optionally includes the end row as well based on the read_last_row parameter.

        Args:
            start_row: The first XML row to include in the extraction.
            end_row: The XML row that marks the end of the extraction range.
            read_last_row: Boolean flag indicating whether to include the end_row in the results.

        Returns:
            A list of XML Tag objects representing all rows in the specified range.
        """
        plate_reader_xml: list[Tag | None] = []
        current = start_row

        # Add the start row
        plate_reader_xml.append(current)

        # Get all rows in between
        while current and current != end_row:
            current = current.find_next("ss:Row")
            if current and current != end_row:
                plate_reader_xml.append(current)  # type: ignore

        # Add the end row if instructed
        if read_last_row and current == end_row:
            plate_reader_xml.append(end_row)

        return plate_reader_xml

    def _parse_plate_reader_xml(self, plate_reader_xml: list[Tag | None]) -> MicroplateData:
        """Parse a list of XML tags into a MicroplateData object.

        Args:
            plate_reader_xml:
                A combination of plate reader metadata and measurements as a list of Tag objects.

        Returns:
            A MicroplateData object containing the parsed plate data.

        Raises:
            ValueError:
                - If the measurement type is unknown. Known measurement types are "Endpoint" and
                  "SpectrumScan".
        """
        # TODO: known issues with metadata:
        # - "Method" appears twice in metadata. It isn't a super relevant field, but it gets
        #   overwritten which could be problematic for some applications.
        # - "Excitation/Emission" extends to multiple lines if more than one pair of wavelengths
        #   are selected.

        is_start_of_well_data = False
        metadata: dict[str, str] = {}
        plate_measurements_xml_rows: list[Tag] = []
        for xml_row in plate_reader_xml:
            if xml_row is not None:
                # Collect metadata
                if not is_start_of_well_data:
                    # "Well data" row signals the start of measurements
                    if "well data" in xml_row.text.lower():
                        is_start_of_well_data = True
                    # Treat all lines prior to measurements as metadata
                    key, *value = xml_row.text.strip().split("\n")
                    metadata[key] = "".join(value)
                # Collect measurements
                else:
                    plate_measurements_xml_rows.append(xml_row)

        # Extract certain fields from metadata
        plate_name = metadata.get("Plate name", "")
        read_time = metadata.get("Read Time")
        timestamp = (
            datetime.strptime(str(read_time), self.datetime_format)
            if read_time is not None
            else None
        )
        well_count_str = metadata.get("Well count")  # --> '96 Wells' or '384 Wells'
        well_count = int(well_count_str.split(" ")[0]) if well_count_str is not None else 96
        plate_type = PlateType(well_count)
        measurement_type = metadata.get("Measurement type")

        # Parse measurement xml data
        if measurement_type == "Endpoint":
            dataframe = self._parse_endpoint_measurements(plate_measurements_xml_rows, plate_type)
        elif measurement_type == "SpectrumScan":
            dataframe = self._parse_spectrum_scan_measurements(
                plate_measurements_xml_rows,
                metadata,
                plate_type,
            )
        elif measurement_type == "Kinetic":
            dataframe = self._parse_kinetic_measurements(
                plate_measurements_xml_rows,
                metadata,
                plate_type,
            )
        else:
            raise ValueError(f"Unknown measurement type: {measurement_type}.")

        # Remove any NaN values and any columns for which all values are NaN
        dataframe = dataframe.dropna(axis=0, how="any", subset="value").dropna(axis=1, how="all")  # type: ignore

        return MicroplateData(
            measurements=dataframe,
            name=plate_name,
            timestamp=timestamp,
            plate_type=plate_type,
            metadata=metadata,
        )

    def _parse_endpoint_measurements(
        self, plate_measurements_xml_rows: list[Tag], plate_type: PlateType
    ) -> pd.DataFrame:  # type: ignore
        """Parse endpoint measurement data from XML into a DataFrame.

        Args:
            plate_measurements_xml_rows: List of XML Tag objects containing measurement data.
            plate_type: The type of microplate (96-well, 384-well, etc.).

        Returns:
            A pandas DataFrame with columns for well IDs, measurement values, and excitation and
            emission wavelengths.
        """
        plate_measurements: list[dict[str, int | float | str]] = []
        for xml_row in plate_measurements_xml_rows:
            # Align xml data with indices
            row_str_data = [re.sub("\n", "", cell.text) for cell in xml_row.find_all("Cell")]
            row_str_indices = [cell.attrs.get("ss:Index") for cell in xml_row.find_all("Cell")]
            start = int(row_str_indices[0]) if row_str_indices[0] is not None else 0
            row_int_indices = forward_fill_indices(row_str_indices, start=start)

            # "Wavelength(Ex/Em)" indicates header row containing excitation/emission data as well
            # as the columns of the wells
            if "Wavelength(Ex/Em)" in row_str_data:
                # Create mapping of {index position: well ID column}
                index_to_well_column: dict[int, int] = {}
                for i, well_column in zip(row_int_indices, row_str_data, strict=True):
                    try:  # not all data in this row is a well column
                        index_to_well_column[i + 1] = int(well_column)
                    except ValueError:
                        continue

                # Try to convert excitation and emission wavelengths to floats
                wavelengths_str = row_str_data[1].split("/")
                wavelengths_nm: list[float] = []
                for wavelength_str in wavelengths_str:
                    match = re.search(r"(\d+)", wavelength_str)
                    if match and match.group(1):
                        wavelengths_nm.append(float(match.group(1)))
                    else:
                        wavelengths_nm.append(np.nan)
                continue

            # First value in subsequent rows of xml is the well ID row
            well_row = row_str_data[0]
            # Iterate through the index and value of each item in the row after the well row
            for i, value in zip(row_int_indices[1:], row_str_data[1:], strict=True):
                well_column = index_to_well_column.get(i)
                if well_column is not None:
                    well = Well(well_row, well_column, plate_type)
                    row_dict = {
                        "well_row": well.row,
                        "well_column": well.column,
                        "well_id": str(well),
                        "value": value_to_float(value),
                        "excitation_nm": wavelengths_nm[0],
                        "emission_nm": wavelengths_nm[1],
                    }
                    plate_measurements.append(row_dict)

        return pd.DataFrame.from_records(plate_measurements)  # type: ignore

    def _parse_spectrum_scan_measurements(
        self,
        plate_measurements_xml_rows: list[Tag],
        metadata: dict[str, Any],
        plate_type: PlateType,
    ) -> pd.DataFrame:  # type: ignore
        """Parse spectrum scan measurement data from XML into a DataFrame.

        Handles both excitation and emission wavelength sweeps based on metadata information.

        Args:
            plate_measurements_xml_rows: List of XML Tag objects containing measurement data.
            metadata: Dictionary of metadata extracted from the XML file.
            plate_type: The type of microplate (96-well, 384-well, etc.).

        Returns:
            A pandas DataFrame with columns for well IDs, measurement values, and excitation and
            emission wavelengths.
        """
        # Make some inferences regarding the excitation/emission scan based on metadata fields
        is_excitation_sweep = True if metadata.get("Excitation sweep") == "True" else False
        if is_excitation_sweep:
            variable_wavelength_field = "excitation_nm"
            constant_wavelength_field = "emission_nm"
            constant_wavelength_nm = float(metadata.get("Emission start"))  # type: ignore
        else:
            variable_wavelength_field = "emission_nm"
            constant_wavelength_field = "excitation_nm"
            constant_wavelength_nm = float(metadata.get("Excitation start"))  # type: ignore

        # Parse measurements
        plate_measurements: list[dict[str, int | float | str]] = []
        for xml_row in plate_measurements_xml_rows:
            # Align xml data with indices
            row_str_data = [re.sub("\n", "", cell.text) for cell in xml_row.find_all("Cell")]
            row_str_indices = [cell.attrs.get("ss:Index") for cell in xml_row.find_all("Cell")]
            start = int(row_str_indices[0]) if row_str_indices[0] is not None else 0
            row_int_indices = forward_fill_indices(row_str_indices, start=start)

            # "Wavelength/Well" indicates header row containing well IDs
            if "Wavelength/Well" in row_str_data:
                # Create mapping of {index position: well ID}
                index_to_well: dict[int, Well] = {}
                for i, well_id in zip(row_int_indices, row_str_data):
                    try:  # not all data in this row is a well column
                        well = Well.from_string(well_id, plate_type)
                        index_to_well[i] = well
                    except ValueError:
                        continue
                continue

            # First value in subsequent rows is the variable wavelength
            variable_wavelength_nm = float(row_str_data[0])
            # Iterate through the index and value of each item in the row
            for i, value in zip(row_int_indices, row_str_data):
                well = index_to_well.get(i)
                if well is not None:
                    row_dict = {
                        "well_row": well.row,
                        "well_column": well.column,
                        "well_id": str(well),
                        "value": value_to_float(value),
                        variable_wavelength_field: variable_wavelength_nm,
                        constant_wavelength_field: constant_wavelength_nm,
                    }
                    plate_measurements.append(row_dict)

        return pd.DataFrame.from_records(plate_measurements)  # type: ignore

    def _parse_kinetic_measurements(
        self,
        plate_measurements_xml_rows: list[Tag],
        metadata: dict[str, Any],
        plate_type: PlateType,
    ) -> pd.DataFrame:  # type: ignore
        """"""
        # Parse measurements
        plate_measurements: list[dict[str, int | float | str]] = []
        for xml_row in plate_measurements_xml_rows:
            # Align xml data with indices
            row_str_data = [re.sub("\n", "", cell.text) for cell in xml_row.find_all("Cell")]
            row_str_indices = [cell.attrs.get("ss:Index") for cell in xml_row.find_all("Cell")]
            start = int(row_str_indices[0]) if row_str_indices[0] is not None else 0
            row_int_indices = forward_fill_indices(row_str_indices, start=start)

            # "Cycle(Seconds)/Well" indicates header row containing well IDs
            if "Cycle(Seconds)/Well" in row_str_data:
                # Create mapping of {index position: well ID}
                index_to_well: dict[int, Well] = {}
                for i, well_id in zip(row_int_indices, row_str_data):
                    try:  # not all data in this row is a well column
                        well = Well.from_string(well_id, plate_type)
                        index_to_well[i] = well
                    except ValueError:
                        continue
                continue

            # First value in subsequent rows is the time (in seconds)
            time_s = float(row_str_data[0])
            # Iterate through the index and value of each item in the row
            for i, value in zip(row_int_indices, row_str_data):
                well = index_to_well.get(i)
                if well is not None:
                    row_dict = {
                        "well_row": well.row,
                        "well_column": well.column,
                        "well_id": str(well),
                        "value": value_to_float(value),
                        "time_s": time_s,
                    }
                    plate_measurements.append(row_dict)

        return pd.DataFrame.from_records(plate_measurements)  # type: ignore


def parse_spectramax_xml(path: Path) -> list[MicroplateData]:
    """An XML parser for interpreting the output of the SpectraMax iD3 microplate reader.

    The SpectraMax iD3 is a microplate reader designed for detecting and quantifying biological
    and chemical reactions in multiwell plates. We use it in the lab for plate-based fluorescence
    assays and optical density measurements. The plate reader outputs these measurements to an XML
    file with a not-so-easy-to-read MS Excel schema, which is why this function exists -- it aims to
    facilitate reading the measurements from plates in batch to aid in the downstream analysis and
    visualization of excitation/emission profiles, growth curves, etc.

    There are three known measurement "modes":
        - Absorption (Abs): for absorption-based assays such as optical density.
        - Fluorescence (Fl): for fluorescence-based assays.
        - Luminescence (unknown flag): for luminescence assays.

    There are also different measurement "types" that are compatible with each measurement mode.
    The format of the XML data (which is annoying enough as is) depends on the measurement type
    (but, thankfully, not also the mode). There are three known measurement types, each with a
    corresponding parser:
        - Single measurement (Endpoint): `_parse_endpoint_measurements()`
        - Spectral scan (SpectrumScan): `_parse_spectrum_scan_measurements()`
        - Timelapse (Kinetic): `_parse_kinetic_measurements()`

    A typical plate reader experiment might involve multiple different measurement modes and
    types that will all be written to a single XML file.
    """
    return SpectraMaxXmlParser(path).parse()
