import logging
from pathlib import Path
from string import ascii_uppercase

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class SpectraMaxXmlParser:
    """

    Attributes:
        soup:
        plate_names:
        num_plates:
    """

    def __init__(self, xml_filepath: Path) -> None:
        xml_text = xml_filepath.read_text()
        self.soup = BeautifulSoup(xml_text, features="xml")

        self.plate_names = self._parse_plate_names()
        self.num_plates = len(self.plate_names)

    def to_formatted_text(self) -> list[str]:
        """Return the XML data in a more legible manner.

        Useful for debugging.
        """
        lines: list[str] = []
        for row in self.soup.find_all("Row"):
            row_contents: list[str] = []
            for cell in row.find_all("Cell"):
                row_contents.append(cell.text)

            line = " | ".join(row_contents)
            lines.append(line)

        return lines

    def _parse_plate_names(self) -> list[str]:
        """"""
        plate_names: list[str] = []
        for row in self.soup.find_all("Row"):
            if "Plate name" in row.text:
                plate_name = [cell.text for cell in row.find_all("Cell")][1]
                message = f"Parsed plate name '{plate_name}' from XML file."
                logger.info(message)
                plate_names.append(plate_name)

        if not plate_names:
            message = "Could not parse 'Plate name' from XML file."
            logger.warning(message)
            plate_names = [""]

        return plate_names

    def _parse_plate_measurements(self) -> dict[str, list[list[tuple[int, str | float]]]]:
        """Parse the XML data for optical density measurements.

        Returns:
            plate_data_mapping:
                A mapping of plate names to plate measurements.
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
                    float(x) if x.replace(".", "", 1).isdigit() else x for x in row_str_data
                ]
                # e.g. [(0, D), (1, 0.114), (6, 0.196)]
                row_of_indexed_measurements: list[tuple[int, str | float]] = list(
                    zip(row_int_indices, row_float_data, strict=True)
                )
                plate_data_mapping[plate_name].append(row_of_indexed_measurements)

        return plate_data_mapping

    def _to_dataframe(self, plate_data: list[list[tuple[int, str | float]]]) -> pd.DataFrame:
        """"""
        dataframe = pd.DataFrame()
        for i, row in enumerate(plate_data):
            for col_index, value in row:
                # replace "" with NaN
                value = value if value != "" else np.nan
                dataframe.loc[i, col_index] = value
        return dataframe

    def get_plate_measurements(self) -> dict[str, pd.DataFrame]:
        """"""
        plate_data_mapping = self._parse_plate_measurements()
        plate_measurements = {}
        for plate_name, plate_data in plate_data_mapping.items():
            dataframe = self._to_dataframe(plate_data)
            plate_measurements[plate_name] = dataframe

        return plate_measurements


def forward_fill_indices(str_indices: list[str | None]) -> list[int]:
    """Forward fill a list of string indices.

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
