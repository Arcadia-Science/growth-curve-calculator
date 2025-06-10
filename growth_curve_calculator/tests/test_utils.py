import numpy as np

from ..utils import forward_fill_indices


def test_forward_fill_indices():
    indices_str = [None, None, None]
    indices_int = forward_fill_indices(indices_str)  # type: ignore
    np.testing.assert_allclose(indices_int, [0, 1, 2])

    indices_str = ["5", None, None]
    indices_int = forward_fill_indices(indices_str, start=2)
    np.testing.assert_allclose(indices_int, [2, 3, 4])

    indices_str = [None, "3", None]
    indices_int = forward_fill_indices(indices_str)
    np.testing.assert_allclose(indices_int, [0, 3, 4])

    indices_str = [None, 2, None, 8, None]
    indices_int = forward_fill_indices(indices_str)
    np.testing.assert_allclose(indices_int, [0, 2, 3, 8, 9])
