import numpy as np
from typing import Tuple



RANDOM_INDEX = {
    1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12,
    6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49,
    11: 1.51, 12: 1.54, 13: 1.56, 14: 1.57, 15: 1.59
}


class ConsistencyChecker:

    def compute_lambda_max(self, matrix: np.ndarray, priority_vector: np.ndarray) -> float:

        n = matrix.shape[0]
        weighted_sum = matrix @ priority_vector
        pv_safe = np.where(priority_vector == 0, 1e-10, priority_vector)
        ratios = weighted_sum / pv_safe
        return float(np.mean(ratios))

    def compute_ci(self, lambda_max: float, n: int) -> float:
        if n <= 1:
            return 0.0
        return (lambda_max - n) / (n - 1)

    def compute_cr(
        self,
        matrix: np.ndarray,
        priority_vector: np.ndarray
    ) -> Tuple[float, float, float]:
        n = matrix.shape[0]
        lambda_max = self.compute_lambda_max(matrix, priority_vector)
        ci = self.compute_ci(lambda_max, n)
        ri = RANDOM_INDEX.get(n, 1.59)  

        if ri == 0:
            cr = 0.0
        else:
            cr = ci / ri

        return ci, cr, lambda_max

    def is_consistent(self, cr: float, threshold: float = 0.1) -> bool:
        return cr <= threshold
