import logging
from pathlib import Path
from string import ascii_uppercase

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class SpectraMaxXmlParser:
    """"""

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

    def _parse_plate_measurements(self) -> dict[str, list[list[tuple[int, str]]]]:
        """

        Returns:
            plate_data_mapping:
                A mapping of plate names to plate measurements.
        """
        plate_data_mapping: dict[str, list[list[tuple[int, str]]]] = {}

        for row in self.soup.find_all("Row"):
            row_str_data = [cell.text for cell in row.find_all("Cell")]
            row_str_indices = [cell.attrs.get("ss:Index") for cell in row.find_all("Cell")]
            # row_int_indices = forward_fill_indices(row_str_indices)
            row_int_indices = range(len(row_str_indices))

            # indicates the start of a new plate --> update plate name
            if "Plate name" in row.text:
                plate_name = [cell.text for cell in row.find_all("Cell")][1]
                plate_data_mapping[plate_name] = []

            # row of OD measurement data
            if row_str_data[0] in ascii_uppercase:
                row_of_indexed_measurements: list[tuple[int, str]] = list(
                    zip(row_int_indices, row_str_data, strict=True)
                )
                plate_data_mapping[plate_name].append(row_of_indexed_measurements)

        return plate_data_mapping

    def get_plate_measurements(self):
        """"""
        pass


# def forward_fill_indices(str_indices: list[str | None]) -> list[int]:
#     """Forward fill a list of string indices.

#     Args:
#         str_indices: A list of indices as string representations of integers mixed and None.

#     Returns:
#         int_indices: A list of indices as integers.

#     Examples:
#         Standard usage:

#         >>> forward_fill_indices(["5", None, None])
#         [0, 1, 2]
#         >>> forward_fill_indices([None, "3", None])
#         [0, 3, 4]
#         >>> forward_fill_indices([None, None, None])
#         [0, 1, 2]
#     """
#     int_indices = [0]
#     for i in str_indices[1:]:
#         if i is not None:
#             int_indices.append(int(i))
#         else:
#             int_indices.append(int_indices[-1] + 1)

#     return int_indices
