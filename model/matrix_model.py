import numpy as np
from typing import List


class MatrixModel:
    def __init__(self, labels: List[str], name: str = ""):
        self.labels = labels
        self.name = name
        n = len(labels)
        self.data = np.ones((n, n))

    def set_value(self, i: int, j: int, value: float):
        self.data[i][j] = value
        if value != 0:
            self.data[j][i] = round(1.0 / value, 6)

    def get_value(self, i: int, j: int) -> float:
        return float(self.data[i][j])

    def to_numpy(self) -> np.ndarray:
        return self.data.copy()

    def from_numpy(self, arr: np.ndarray):
        self.data = arr.copy()

    def size(self) -> int:
        return len(self.labels)
