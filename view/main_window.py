import customtkinter as ctk
from viewmodel.ahp_viewmodel import AHPViewModel
from view.goal_view import GoalView
from view.data_input_view import DataInputView
from view.result_view import ResultView


STEPS = ["1. Setup", "2. Enter Data", "3. Results"]


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AHP System")
        self.geometry("1200x800")
        self.minsize(950, 680)

        self.vm = AHPViewModel()
        self.current_step = 0
        self._build_layout()
        self._show_step(0)

    def _build_layout(self):
        self.sidebar = ctk.CTkFrame(self, width=210, corner_radius=0, fg_color="#0d1b2a")
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        ctk.CTkLabel(
            self.sidebar,
            text="AHP\nDecision System",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#a8dadc"
        ).pack(pady=(30, 8))
        ctk.CTkLabel(
            self.sidebar, text="Powered by Mistral AI",
            font=ctk.CTkFont(size=11), text_color="#457b9d"
        ).pack(pady=(0, 30))

        self.step_labels = []
        for i, step in enumerate(STEPS):
            lbl = ctk.CTkLabel(
                self.sidebar, text=f"  {step}",
                font=ctk.CTkFont(size=13), text_color="gray",
                anchor="w", width=190
            )
            lbl.pack(pady=8, padx=10, anchor="w")
            self.step_labels.append(lbl)

        ctk.CTkLabel(self.sidebar, text="").pack(expand=True)
        self.status_label = ctk.CTkLabel(
            self.sidebar, text="Ready",
            font=ctk.CTkFont(size=11), text_color="#457b9d", wraplength=185
        )
        self.status_label.pack(pady=20, padx=10)

        self.vm.on_status_update = self._update_status
        self.vm.on_error = self._show_error


        self.content = ctk.CTkFrame(self, fg_color="#12121c", corner_radius=0)
        self.content.pack(side="right", fill="both", expand=True)

        self.goal_view = GoalView(
            self.content,
            on_next=self._on_goal_next,
            fg_color="transparent"
        )
        self.data_view = DataInputView(
            self.content,
            viewmodel=self.vm,
            on_next=self._on_data_next,
            on_back=lambda: self._show_step(0),
            fg_color="transparent"
        )
        self.result_view = ResultView(
            self.content,
            viewmodel=self.vm,
            on_restart=self._restart,
            fg_color="transparent"
        )
        self.views = [self.goal_view, self.data_view, self.result_view]

    def _show_step(self, step: int):
        for v in self.views:
            v.pack_forget()
        for i, lbl in enumerate(self.step_labels):
            if i == step:
                lbl.configure(text_color="#a8dadc", font=ctk.CTkFont(size=13, weight="bold"))
            elif i < step:
                lbl.configure(text_color="#2d6a4f", font=ctk.CTkFont(size=13))
            else:
                lbl.configure(text_color="gray", font=ctk.CTkFont(size=13))
        self.current_step = step
        self.views[step].pack(fill="both", expand=True)

    def _on_goal_next(self, goal: str, criteria: list, alternatives: list,
                      pdf_matrix=None):
        self.vm.set_goal(goal)
        self.vm.set_criteria(criteria)
        self.vm.set_alternatives(alternatives)
        self.vm.initialize_matrices()
        self.data_view.refresh(pdf_matrix=pdf_matrix)
        self._show_step(1)

    def _on_data_next(self):
        self.vm.on_calculation_complete = lambda r: self.after(0, self._show_results)
        self.vm.run_calculation()

    def _show_results(self):
        self.result_view.refresh()
        self._show_step(2)

    def _restart(self):
        self.vm.reset()
        for v in self.views:
            v.pack_forget()
            v.destroy()
        self.goal_view = GoalView(self.content, on_next=self._on_goal_next, fg_color="transparent")
        self.data_view = DataInputView(
            self.content, viewmodel=self.vm,
            on_next=self._on_data_next, on_back=lambda: self._show_step(0),
            fg_color="transparent"
        )
        self.result_view = ResultView(self.content, viewmodel=self.vm,
                                      on_restart=self._restart, fg_color="transparent")
        self.views = [self.goal_view, self.data_view, self.result_view]
        self.vm.on_status_update = self._update_status
        self.vm.on_error = self._show_error
        self._show_step(0)

    def _update_status(self, msg: str):
        self.after(0, lambda: self.status_label.configure(text=msg))

    def _show_error(self, msg: str):
        self.after(0, self._display_error, msg)

    def _display_error(self, msg: str):
        err = ctk.CTkToplevel(self)
        err.title("Error")
        err.geometry("420x160")
        ctk.CTkLabel(err, text=" Error",
                     font=ctk.CTkFont(size=16, weight="bold"), text_color="#e63946").pack(pady=(20, 8))
        ctk.CTkLabel(err, text=msg, wraplength=380, text_color="#ccc").pack(pady=4)
        ctk.CTkButton(err, text="OK", command=err.destroy, width=100).pack(pady=12)
