import numpy as np
import threading
from typing import List, Dict, Optional, Callable
from model.ahp_model import AHPModel
from services.ahp_engine import AHPEngine
from services.llm_service import LLMService


class AHPViewModel:
    def __init__(self):
        self.model = AHPModel()
        self.engine = AHPEngine()
        self.llm = LLMService()

        self.on_criteria_generated: Optional[Callable] = None
        self.on_calculation_complete: Optional[Callable] = None
        self.on_explanation_token: Optional[Callable] = None
        self.on_explanation_complete: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        self.on_status_update: Optional[Callable] = None


    def set_goal(self, goal: str):
        self.model.goal = goal.strip()

    def set_criteria(self, criteria: List[str]):
        self.model.criteria = [c.strip() for c in criteria if c.strip()]

    def set_alternatives(self, alternatives: List[str]):
        self.model.alternatives = [a.strip() for a in alternatives if a.strip()]

    def initialize_matrices(self):
        
        self.model.initialize_all_matrices()



    def update_criteria_matrix(self, i: int, j: int, value: float):
        self.model.set_criteria_comparison(i, j, value)

    def update_alt_matrix(self, criterion: str, i: int, j: int, value: float):
        self.model.set_alt_comparison(criterion, i, j, value)

    def get_criteria_matrix(self) -> Optional[np.ndarray]:
        return self.model.criteria_matrix

    def get_alt_matrix(self, criterion: str) -> Optional[np.ndarray]:
        return self.model.alt_matrices.get(criterion)



    def generate_criteria_async(self, num_criteria: int = 5):
        
        def task():
            if self.on_status_update:
                self.on_status_update("Generating criteria with Mistral...")
            raw = self.llm.generate_criteria(self.model.goal, num_criteria)
            if self.on_criteria_generated:
                self.on_criteria_generated(raw)
            if self.on_status_update:
                self.on_status_update("Criteria generated.")

        threading.Thread(target=task, daemon=True).start()


    def run_calculation(self):
        
        if not self.model.is_ready_for_calculation():
            if self.on_error:
                self.on_error("Please ensure goal, criteria, alternatives, and matrices are all set.")
            return

        try:
            results = self.engine.run_full_ahp(
                self.model.criteria,
                self.model.alternatives,
                self.model.criteria_matrix,
                self.model.alt_matrices
            )
            self.model.results = results
            if self.on_calculation_complete:
                self.on_calculation_complete(results)
        except Exception as e:
            if self.on_error:
                self.on_error(f"Calculation error: {str(e)}")

    
    def explain_results_async(self, language: str = "en"):
        
        if not self.model.results:
            if self.on_error:
                self.on_error("Run calculation first.")
            return

        def task():
            results = self.model.results
            crit_pv = results["criteria_priority_vector"]
            if self.on_status_update:
                self.on_status_update("Generating AI explanation...")

            def token_callback(token):
                if self.on_explanation_token:
                    self.on_explanation_token(token)

            self.llm.explain_results(
                goal=self.model.goal,
                criteria=self.model.criteria,
                criteria_weights=crit_pv.tolist(),
                alternatives=self.model.alternatives,
                scores=results["weighted_scores"].tolist(),
                ranking=results["ranking"],
                language=language,
                on_token=token_callback
            )
            if self.on_explanation_complete:
                self.on_explanation_complete()
            if self.on_status_update:
                self.on_status_update("Explanation complete.")

        threading.Thread(target=task, daemon=True).start()



    def export_csv(self, output_dir: str) -> str:
        from utils.helpers import export_all_results_to_csv
        if self.model.results:
            return export_all_results_to_csv(self.model.results, output_dir)
        return ""

    def export_pdf(self, filepath: str, explanation: str) -> bool:
        from utils.helpers import generate_pdf_report
        if self.model.results:
            return generate_pdf_report(
                self.model.results, self.model.goal, explanation, filepath
            )
        return False



    def get_criteria(self) -> List[str]:
        return self.model.criteria

    def get_alternatives(self) -> List[str]:
        return self.model.alternatives

    def get_goal(self) -> str:
        return self.model.goal

    def get_results(self) -> Optional[Dict]:
        return self.model.results

    def reset(self):
        self.model.reset()



    def set_raw_data(self, raw_matrix, direction_flags: dict):
        self.model.raw_matrix = raw_matrix
        self.model.direction_flags = direction_flags

    def get_raw_data(self):
        return getattr(self.model, "raw_matrix", None)

    def get_direction_flags(self):
        return getattr(self.model, "direction_flags", {})
