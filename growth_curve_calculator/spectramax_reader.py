import logging
from dataclasses import dataclass
from pathlib import Path
from string import ascii_uppercase

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


@dataclass
class SpectraMaxData:
    """A dataclass for SpectraMax iD3 microplate reader data.

    The SpectraMax iD3 is a microplate reader designed for detecting and quantifying biological
    and chemical reactions in multiwell plates. We use it in the lab primarily for optical density
    (OD) measurements of cell cultures, which can be used as a proxy to measure cell growth.
    The plate reader outputs OD measurements to an XML file with a not-so-easy-to-read MS Excel
    schema, which is why this class exists -- it aims to facilitate reading the OD measurements
    from plates in batch to aid in the downstream analysis and visualization of growth curves.

    Attributes:
        read_times: A list of timestamps of when the plate measurements were made.
        plate_names: A list of names of each plate measured.
        plate_measurements: A mapping of plate names to dataframes of optical density measurements.
        num_plates: The number of plate measurements present in the XML file.
    """

    read_times: list[pd.Timestamp]
    plate_names: list[str]
    plate_measurements: dict[str, pd.DataFrame]

    @property
    def num_plates(self) -> int:
        return len(self.plate_names)

    @classmethod
    def from_xml(cls, xml_filepath: Path | str) -> "SpectraMaxData":
        return SpectraMaxXmlParser(xml_filepath).parse()


class SpectraMaxXmlParser:
    """An XML parser for interpreting the output of the SpectraMax iD3 microplate reader.

    The SpectraMax iD3 is a microplate reader designed for detecting and quantifying biological
    and chemical reactions in multiwell plates. We use it in the lab primarily for optical density
    (OD) measurements of cell cultures, which can be used as a proxy to measure cell growth.
    The plate reader outputs OD measurements to an XML file with a not-so-easy-to-read MS Excel
    schema, which is why this class exists -- it aims to facilitate reading the OD measurements
    from plates in batch to aid in the downstream analysis and visualization of growth curves.

    Attributes:
        soup: A BeautifulSoup object representing the parsed XML file.
    """

    def __init__(self, xml_filepath: Path | str) -> None:
        xml_filepath = Path(xml_filepath)
        xml_text = xml_filepath.read_text()
        self.soup = BeautifulSoup(xml_text, features="xml")

    def parse(self) -> SpectraMaxData:
        return SpectraMaxData(
            read_times=self._parse_read_times(),
            plate_names=self._parse_plate_names(),
            plate_measurements=self.get_plate_measurements(),
        )

    def _to_formatted_text(self) -> list[str]:
        """Return the XML data in a more legible manner (useful for debugging)."""
        lines: list[str] = []
        for row in self.soup.find_all("Row"):
            row_contents: list[str] = []
            for cell in row.find_all("Cell"):
                row_contents.append(cell.text)

            line = " | ".join(row_contents)
            lines.append(line)

        return lines

    def _parse_read_times(self) -> list[pd.Timestamp]:
        """Parse read times from XML data."""
        read_times: list[pd.Timestamp] = []
        for row in self.soup.find_all("Row"):
            if "Read Time" in row.text:
                read_time = [cell.text for cell in row.find_all("Cell")][1]
                read_times.append(pd.Timestamp(read_time))

        if not read_times:
            message = "Could not parse 'Read Time' from XML file."
            logger.warning(message)

        return read_times

    def _parse_plate_names(self) -> list[str]:
        """Parse plate names from XML data."""
        plate_names: list[str] = []
        for row in self.soup.find_all("Row"):
            if "Plate name" in row.text:
                plate_name = [cell.text for cell in row.find_all("Cell")][1]
                plate_names.append(plate_name)

        if not plate_names:
            message = "Could not parse 'Plate name' from XML file."
            logger.warning(message)
            plate_names = [""]

        return plate_names

    def _parse_plate_measurements(self) -> dict[str, list[list[tuple[int, str | float]]]]:
        """Parse the XML data for optical density measurements.

        The output `plate_data_mapping` is a bit wonky. It takes the form of a list of rows
        in which each item in the row is an optical density measurement (either a float or a
        string that cannot easily be converted to a float e.g. "C" or "") paired with its index.
        """
        plate_data_mapping: dict[str, list[list[tuple[int, str | float]]]] = {}

        for row in self.soup.find_all("Row"):
            row_str_data = [cell.text for cell in row.find_all("Cell")]
            row_str_indices = [cell.attrs.get("ss:Index") for cell in row.find_all("Cell")]
            row_int_indices = forward_fill_indices(row_str_indices)

            # indicates the start of a new plate --> update plate name
            if "Plate name" in row.text:
                plate_name = [cell.text for cell in row.find_all("Cell")][1]
                plate_data_mapping[plate_name] = []

            # row of OD measurement data
            if row_str_data and row_str_data[0] in ascii_uppercase:
                # convert measurements to float where possible
                row_float_data = [
                    float(x) if x.replace(".", "", 1).isdigit() or "E-" in x else x
                    for x in row_str_data
                ]
                # e.g. [(0, D), (1, 0.114), (6, 0.196)]
                row_of_indexed_measurements: list[tuple[int, str | float]] = list(
                    zip(row_int_indices, row_float_data, strict=True)
                )
                plate_data_mapping[plate_name].append(row_of_indexed_measurements)

        return plate_data_mapping

    def _to_dataframe(self, plate_data: list[list[tuple[int, str | float]]]) -> pd.DataFrame:
        """Converts plate measurements parsed by `_parse_plate_measurements` to a pandas
        DataFrame."""
        dataframe = pd.DataFrame()
        for i, row in enumerate(plate_data):
            for col_index, value in row:
                # replace "" and "Error" with NaN
                if value == "" or value == "Error":
                    value = np.nan
                dataframe.loc[i, col_index] = value
        dataframe_reindexed = dataframe.set_index(0).rename_axis(None)  # type: ignore
        dataframe_filtered = dataframe_reindexed.dropna(axis=1, how="all").dropna(axis=0, how="all")  # type: ignore
        return dataframe_filtered

    def get_plate_measurements(self) -> dict[str, pd.DataFrame]:
        """Get optical density measurements from XML file.

        Returns:
            plate_data_mapping:
                A mapping of plate names to plate measurements as a pandas DataFrame. Example:

                {
                    'Phaeo':
                            1      2      3      4      5      6      7      8      9
                        A  0.164  0.190  0.438  0.375  0.224  0.241  0.185  0.117  0.111
                        B  0.173  0.196  0.454  0.339  0.212  0.223  0.206  0.149  0.136,
                    'Protococcus':
                            1      2      3      4      5      6      7      8      9
                        A  0.098  0.067  0.055  0.057  0.199  0.049  0.044  0.033  0.035
                        B  0.106  0.091  0.055  0.054  0.247  0.047  0.042  0.038  0.045
                }
        """
        plate_data_mapping = self._parse_plate_measurements()
        plate_measurements = {}
        for plate_name, plate_data in plate_data_mapping.items():
            dataframe = self._to_dataframe(plate_data)
            plate_measurements[plate_name] = dataframe
        return plate_measurements


def forward_fill_indices(str_indices: list[str | None]) -> list[int]:
    """Forward fill a list of string indices with first index position as 0.

    Args:
        str_indices: A list of indices as string representations of integers mixed and None.

    Returns:
        int_indices: A list of forward filled indices as integers starting at 0.

    Examples:
        >>> forward_fill_indices(["5", None, None])
        [0, 1, 2]
        >>> forward_fill_indices([None, "3", None])
        [0, 3, 4]
        >>> forward_fill_indices([None, None, None])
        [0, 1, 2]
    """
    int_indices = [0]
    for i in str_indices[1:]:
        if i is not None:
            int_indices.append(int(i))
        else:
            int_indices.append(int_indices[-1] + 1)

    return int_indices
