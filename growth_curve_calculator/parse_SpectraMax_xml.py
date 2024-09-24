import logging
from pathlib import Path

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class SpectraMaxXmlParser:
    """"""

    def __init__(self, xml_filepath: Path) -> None:
        xml_text = xml_filepath.read_text()
        self.soup = BeautifulSoup(xml_text, features="xml")

        self.plate_names = self._parse_plate_names()
        self.num_plates = len(self.plate_names)

    def to_dict(self):
        """"""
        instrument_data = {}
        plate_data = {plate_name: {} for plate_name in self.plate_names}
        plate_index = 0

        for row in self.soup.find_all("Row"):
            row_data = [cell.text for cell in row.find_all("Cell")]
            # skip empty row
            if not row_data:
                continue

            key = row_data[0]
            if not row_data[1:]:
                value = ""
            else:
                value = row_data[1:] if len(row_data[1:]) > 2 else row_data[1]

            # skip problematic line
            if "Plate  (" in row.text:
                continue

            # indicates the start of a new plate --> update plate name
            if "Plate name" in row.text:
                plate_name = [cell.text for cell in row.find_all("Cell")][1]
                plate_index += 1

            if not plate_index:
                instrument_data[key] = value
            else:
                plate_data[plate_name][key] = value

        return {**instrument_data, **plate_data}

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

    def _parse_OD_measurements(self):
        """"""

    def get_OD_measurements(self):
        """"""
