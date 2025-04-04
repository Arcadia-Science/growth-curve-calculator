import numpy as np


def forward_fill_indices(str_indices: list[str | None], start: int = 0) -> list[int]:
    """Forward fill a list of string indices.

    Args:
        str_indices: A list of indices as string representations of integers mixed and None.
        start: An integer indicating the starting position.

    Returns:
        int_indices: A list of forward filled indices as integers starting with `start`.

    Examples:
        >>> forward_fill_indices(["5", None, None])
        [0, 1, 2]
        >>> forward_fill_indices(["5", None, None], start=2)
        [2, 3, 4]
        >>> forward_fill_indices([None, "3", None])
        [0, 3, 4]
        >>> forward_fill_indices([None, "2", None, "8", None])
        [0, 2, 3, 8, 9]
    """
    int_indices = [start]
    for i in str_indices[1:]:
        if i is not None:
            int_indices.append(int(i))
        else:
            int_indices.append(int_indices[-1] + 1)
    return int_indices


def value_to_float(value: str) -> float:
    """Convert a string value to float, returning NaN if conversion fails.

    Args:
        value: String representation of a number.

    Returns:
        Float value or NaN if conversion fails.
    """
    try:
        return float(value)
    except ValueError:
        return np.nan
