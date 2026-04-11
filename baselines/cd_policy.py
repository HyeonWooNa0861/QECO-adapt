from __future__ import annotations

import numpy as np


class CDBinaryOffloadPolicy:
    """Independent baseline wrapper for the DROO paper's CD method."""

    def __init__(self):
        from optimization import cd_method

        self._cd_method = cd_method

    def select_mode(self, channel_vector) -> np.ndarray:
        _, best_mode = self._cd_method(channel_vector)
        return np.asarray(best_mode, dtype=int)
