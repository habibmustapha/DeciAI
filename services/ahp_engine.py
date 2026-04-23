import numpy as np
from typing import List, Dict, Tuple
from services.consistency import ConsistencyChecker


class AHPEngine:
    def __init__(self):
        self.consistency_checker = ConsistencyChecker()

    def normalize_matrix(self, matrix: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:

        n = matrix.shape[0]
        col_sums = matrix.sum(axis=0)
        col_sums = np.where(col_sums == 0, 1e-10, col_sums)
        normalized = matrix / col_sums

        priority_vector = normalized.mean(axis=1)
        return normalized, priority_vector

    def compute_weighted_scores(
        self,
        criteria_priorities: np.ndarray,
        alt_priorities_per_criterion: List[np.ndarray]
    ) -> np.ndarray:
        n_alt = len(alt_priorities_per_criterion[0])
        n_crit = len(criteria_priorities)
        scores = np.zeros(n_alt)

        for j in range(n_crit):
            scores += criteria_priorities[j] * alt_priorities_per_criterion[j]

        return scores

    def rank_alternatives(
        self,
        alternatives: List[str],
        scores: np.ndarray
    ) -> List[Tuple[int, str, float]]:
        indexed = [(i, alternatives[i], scores[i]) for i in range(len(alternatives))]
        ranked = sorted(indexed, key=lambda x: x[2], reverse=True)
        return [(rank + 1, name, score) for rank, (i, name, score) in enumerate(ranked)]

    def run_full_ahp(
        self,
        criteria: List[str],
        alternatives: List[str],
        criteria_matrix: np.ndarray,
        alt_matrices: Dict[str, np.ndarray]
    ) -> Dict:
        results = {
            "criteria": criteria,
            "alternatives": alternatives,
            "criteria_matrix": criteria_matrix,
            "alt_matrices": alt_matrices,
            "normalized_criteria_matrix": None,
            "criteria_priority_vector": None,
            "normalized_alt_matrices": {},
            "alt_priority_vectors": {},
            "weighted_scores": None,
            "ranking": None,
            "criteria_consistency": None,
            "alt_consistencies": {},
            "errors": []
        }


        norm_crit, crit_pv = self.normalize_matrix(criteria_matrix)
        results["normalized_criteria_matrix"] = norm_crit
        results["criteria_priority_vector"] = crit_pv

        ci, cr, lmax = self.consistency_checker.compute_cr(criteria_matrix, crit_pv)
        results["criteria_consistency"] = {"CI": ci, "CR": cr, "lambda_max": lmax}


        alt_priorities = []
        for crit in criteria:
            matrix = alt_matrices.get(crit)
            if matrix is None:
                results["errors"].append(f"Missing matrix for criterion: {crit}")
                continue

            norm_alt, alt_pv = self.normalize_matrix(matrix)
            results["normalized_alt_matrices"][crit] = norm_alt
            results["alt_priority_vectors"][crit] = alt_pv
            alt_priorities.append(alt_pv)

            ci_a, cr_a, lmax_a = self.consistency_checker.compute_cr(matrix, alt_pv)
            results["alt_consistencies"][crit] = {"CI": ci_a, "CR": cr_a, "lambda_max": lmax_a}

        if alt_priorities:
            scores = self.compute_weighted_scores(crit_pv, alt_priorities)
            results["weighted_scores"] = scores
            results["ranking"] = self.rank_alternatives(alternatives, scores)

        return results
