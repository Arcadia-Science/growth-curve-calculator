from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import pandas as pd


class PlateType(Enum):
    """Enum representing different plate formats."""

    PLATE_96 = 96
    PLATE_384 = 384


@dataclass
class MicroplateData:
    """Representation of a microplate dataset."""

    measurements: pd.DataFrame
    name: str | None = None
    timestamp: datetime | None = None
    plate_type: PlateType = PlateType.PLATE_96
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Well:
    """Representation of a well in a microplate.

    Attributes:
        row: A single uppercase letter representing the row (A-H for 96-well, A-P for 384-well).
        column: An integer representing the column (1-12 for 96-well, 1-24 for 384-well).
        plate_type: The type of plate this well belongs to (96 or 384 well).
        content: Optional description of the well's contents.
    """

    row: str
    column: int
    plate_type: PlateType = PlateType.PLATE_96
    content: str | None = None

    def __post_init__(self):
        """Validate the row and column after initialization."""
        # Ensure row is a single uppercase letter
        if not isinstance(self.row, str) or len(self.row) != 1 or not "A" <= self.row <= "Z":
            raise ValueError("Row must be a single uppercase letter (A-Z).")
        if not isinstance(self.column, int):
            raise ValueError("Column must be an integer.")

        # Validate row and column based on plate type
        if self.plate_type == PlateType.PLATE_96:
            if not "A" <= self.row <= "H":
                raise ValueError("For 96-well plates, row must be between A and H.")
            if not 1 <= self.column <= 12:
                raise ValueError("For 96-well plates, column must be between 1 and 12.")
        elif self.plate_type == PlateType.PLATE_384:
            if not "A" <= self.row <= "P":
                raise ValueError("For 384-well plates, row must be between A and P.")
            if not 1 <= self.column <= 24:
                raise ValueError("For 384-well plates, column must be between 1 and 24.")

    def __str__(self) -> str:
        """Return string representation of the well with the column integer padded with a zero."""
        return f"{self.row}{self.column:02d}"

    def __repr__(self) -> str:
        """Return a string that could be used to recreate this object."""
        return f"Well(row='{self.row}', column={self.column}, plate_type={self.plate_type})"

    @classmethod
    def from_string(cls, well_id: str, plate_type: PlateType = PlateType.PLATE_96) -> Well:
        """Create a Well object from a string like "A01" or "H12".

        Args:
            well_id: String representation of well (e.g., "A01", "H12").
            plate_type: The type of plate this well belongs to.

        Raises:
            ValueError:
                - If the `well_id` format is invalid.
        """
        if not well_id or len(well_id) < 2:
            raise ValueError("Well ID must be at least 2 characters (e.g., 'A1' or 'A01').")

        row = well_id[0].upper()
        try:
            column = int(well_id[1:])
        except ValueError:
            raise ValueError from ValueError(f"Could not parse column number from '{well_id}'.")

        return cls(row=row, column=column, plate_type=plate_type)
