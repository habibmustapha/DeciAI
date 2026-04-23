import customtkinter as ctk
from typing import Callable, List


class CriteriaView(ctk.CTkFrame):
    def __init__(self, parent, viewmodel, on_next: Callable, on_back: Callable, **kwargs):
        super().__init__(parent, **kwargs)
        self.vm = viewmodel
        self.on_next = on_next
        self.on_back = on_back
        self.criteria_entries: List[ctk.CTkEntry] = []
        self._build_ui()
        self._setup_callbacks()

    def _build_ui(self):
        
        ctk.CTkLabel(
            self, text="Define Criteria",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=(20, 5))

        
        self.goal_label = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=13), text_color="#a8dadc"
        )
        self.goal_label.pack()

        
        mode_frame = ctk.CTkFrame(self)
        mode_frame.pack(fill="x", padx=40, pady=15)
        ctk.CTkLabel(
            mode_frame, text="Criteria Mode:", font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", pady=(10, 5), padx=10)

        self.mode_var = ctk.StringVar(value="manual")
        mode_row = ctk.CTkFrame(mode_frame, fg_color="transparent")
        mode_row.pack(fill="x", padx=10, pady=(0, 10))
        for text, val in [("✍️  Manual Entry", "manual"), ("AI-Generated (Mistral)", "ai")]:
            ctk.CTkRadioButton(
                mode_row, text=text, variable=self.mode_var, value=val,
                command=self._on_mode_change
            ).pack(side="left", padx=15)

        self.ai_frame = ctk.CTkFrame(self, fg_color="#1a1a2e")
        ctk.CTkLabel(self.ai_frame, text="Number of criteria:").pack(
            side="left", padx=10, pady=10)
        self.ai_num_var = ctk.StringVar(value="5")
        ctk.CTkComboBox(
            self.ai_frame, values=["3", "4", "5", "6", "7"],
            variable=self.ai_num_var, width=80
        ).pack(side="left", padx=5, pady=10)
        self.ai_btn = ctk.CTkButton(
            self.ai_frame, text="🤖 Generate Criteria",
            command=self._generate_ai_criteria,
            fg_color="#4a0e8f", hover_color="#7b2d8b"
        )
        self.ai_btn.pack(side="left", padx=10, pady=10)
        self.ai_status = ctk.CTkLabel(self.ai_frame, text="", text_color="#a8dadc")
        self.ai_status.pack(side="left", padx=5)


        ctk.CTkLabel(
            self, text="Criteria List (edit as needed):",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", padx=40, pady=(10, 4))

        self.criteria_scroll = ctk.CTkScrollableFrame(self, height=220)
        self.criteria_scroll.pack(fill="x", padx=40)

        for _ in range(3):
            self._add_criterion_row()

        ctk.CTkButton(
            self, text="+ Add Criterion",
            command=self._add_criterion_row,
            width=160, fg_color="#2d6a4f", hover_color="#1b4332"
        ).pack(pady=8)

        nav = ctk.CTkFrame(self, fg_color="transparent")
        nav.pack(pady=15)
        ctk.CTkButton(
            nav, text="← Back", command=self.on_back,
            width=120, fg_color="#555", hover_color="#777"
        ).pack(side="left", padx=10)
        ctk.CTkButton(
            nav, text="Next: Pairwise Comparisons →",
            command=self._handle_next,
            height=44, font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#1d3557", hover_color="#457b9d"
        ).pack(side="left", padx=10)

    def _setup_callbacks(self):
        self.vm.on_criteria_generated = self._on_criteria_received
        self.vm.on_status_update = self._on_status

    def _on_mode_change(self):

        if self.mode_var.get() == "ai":
            self.ai_frame.pack(fill="x", padx=40, pady=5)
        else:
            self.ai_frame.pack_forget()

    def _add_criterion_row(self, text: str = ""):
        row = ctk.CTkFrame(self.criteria_scroll, fg_color="transparent")
        row.pack(fill="x", pady=3)

        entry = ctk.CTkEntry(row, placeholder_text="e.g. Salary & Benefits", height=36)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        if text:
            entry.insert(0, text)

        def remove(r=row, e=entry):
            if e in self.criteria_entries:
                self.criteria_entries.remove(e)
            r.destroy()

        ctk.CTkButton(
            row, text="✕", width=36, height=36,
            fg_color="#6b2737", hover_color="#9b2335",
            command=remove
        ).pack(side="right")

        self.criteria_entries.append(entry)

    def _generate_ai_criteria(self):
        num = int(self.ai_num_var.get())
        self.ai_btn.configure(state="disabled", text="Generating...")
        self.vm.generate_criteria_async(num)

    def _on_criteria_received(self, criteria_list: list):
        for widget in self.criteria_scroll.winfo_children():
            widget.destroy()
        self.criteria_entries.clear()
        for item in criteria_list:
            name = item.get("name", "") if isinstance(item, dict) else str(item)
            self._add_criterion_row(name)
        self.ai_btn.configure(state="normal", text="Generate Criteria")
        self.ai_status.configure(text=f"✓ {len(criteria_list)} criteria generated")

    def _on_status(self, msg: str):
        if hasattr(self, "ai_status"):
            self.ai_status.configure(text=msg)

    def refresh(self, goal: str):
        self.goal_label.configure(text=f"Goal: {goal}")

    def _handle_next(self):
        criteria = [e.get().strip() for e in self.criteria_entries if e.get().strip()]
        if len(criteria) < 2:
            ctk.CTkLabel(self, text="⚠ Add at least 2 criteria.", text_color="#e63946").pack()
            return
        self.on_next(criteria)
