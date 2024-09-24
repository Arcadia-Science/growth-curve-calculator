import logging
from pathlib import Path

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class SpectraMaxXmlParser:
    """"""

    def __init__(self, xml_filepath: Path) -> None:
        xml_text = xml_filepath.read_text()
        self.soup = BeautifulSoup(xml_text, features="xml")

    def to_dict(self):
        """"""

    def _parse_plate_name(self):
        """"""
        plate_name_data = None
        for row in self.soup.find_all("Row"):
            for cell in row.find_all("Cell"):
                if "Plate name" in cell.find("Data"):
                    plate_name_data = [cell.find("Data").text for cell in row.find_all("Cell")]

        if plate_name_data is None:
            message = "Could not parse 'Plate name' from XML file."
            raise ValueError(message)
        elif len(plate_name_data) < 2:
            message = "'Plate name' not provided in XML file."
            logger.warning(message)
            plate_name = ""
        elif len(plate_name_data) == 2:
            plate_name = plate_name_data[1]
            message = f"Parsed '{plate_name}' for 'Plate name' from XML file."
            logger.info(message)
        else:
            message = f"Multiple plate names provided in XML file: {plate_name_data}."
            raise ValueError(message)

        return plate_name

    def _parse_OD_measurements(self):
        """"""

    def get_organism_name(self):
        """"""
        return self._parse_plate_name()

    def get_OD_measurements(self):
        """"""
