import numpy as np
from typing import List, Dict, Optional


class AHPModel:
    def __init__(self):
        self.goal: str = ""
        self.criteria: List[str] = []
        self.alternatives: List[str] = []
        self.criteria_matrix: Optional[np.ndarray] = None
        self.alt_matrices: Dict[str, np.ndarray] = {}
        self.results: Optional[Dict] = None

    def initialize_criteria_matrix(self):
        n = len(self.criteria)
        self.criteria_matrix = np.ones((n, n))

    def initialize_alt_matrix(self, criterion: str):
        n = len(self.alternatives)
        self.alt_matrices[criterion] = np.ones((n, n))

    def initialize_all_matrices(self):
        self.initialize_criteria_matrix()
        for c in self.criteria:
            self.initialize_alt_matrix(c)

    def set_criteria_comparison(self, i: int, j: int, value: float):
        if self.criteria_matrix is not None:
            self.criteria_matrix[i][j] = value
            self.criteria_matrix[j][i] = 1.0 / value if value != 0 else 1.0

    def set_alt_comparison(self, criterion: str, i: int, j: int, value: float):
        if criterion in self.alt_matrices:
            self.alt_matrices[criterion][i][j] = value
            self.alt_matrices[criterion][j][i] = 1.0 / value if value != 0 else 1.0

    def is_ready_for_calculation(self) -> bool:
        return (
            bool(self.goal) and
            len(self.criteria) >= 2 and
            len(self.alternatives) >= 2 and
            self.criteria_matrix is not None and
            len(self.alt_matrices) == len(self.criteria)
        )

    def reset(self):
        self.__init__()
