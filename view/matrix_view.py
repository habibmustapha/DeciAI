import customtkinter as ctk
import numpy as np
from typing import List, Callable, Dict


def parse_value(text: str, fallback: float = 1.0) -> float:

    text = text.strip()
    try:
        if "/" in text:
            parts = text.split("/")
            val = float(parts[0]) / float(parts[1])
        else:
            val = float(text)
        # Clamp to valid AHP range
        val = max(1/9, min(9.0, val))
        return round(val, 6)
    except (ValueError, ZeroDivisionError):
        return fallback


def format_reciprocal(val: float) -> str:

    if val <= 0:
        return "1"
    recip = 1.0 / val
    if abs(recip - round(recip)) < 0.001:
        r = int(round(recip))
        return f"1/{int(round(val))}" if r == 1 and val > 1 else str(r)
    return f"{recip:.3f}"


def scores_to_pairwise(scores: np.ndarray) -> np.ndarray:

    n = len(scores)
    mat = np.ones((n, n))
    for i in range(n):
        for j in range(n):
            mat[i][j] = scores[i] / scores[j] if scores[j] != 0 else 1.0
    return mat



CELL_W   = 72
LABEL_W  = 130
CELL_H   = 34
FONT_SM  = ("", 11)




class CriteriaPairwiseWidget(ctk.CTkFrame):

    def __init__(self, parent, labels: List[str], on_change: Callable = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.labels   = labels
        self.n        = len(labels)
        self.on_change = on_change
        self._entries: Dict[tuple, ctk.CTkEntry] = {}   
        self._recip_labels: Dict[tuple, ctk.CTkLabel] = {}  
        self._build()

    def _build(self):

        ctk.CTkLabel(self, text="", width=LABEL_W).grid(row=0, column=0, padx=2, pady=2)


        for j, lbl in enumerate(self.labels):
            ctk.CTkLabel(
                self, text=lbl[:14],
                font=ctk.CTkFont(size=11, weight="bold"),
                width=CELL_W, anchor="center",
                fg_color="#1d3557", corner_radius=4
            ).grid(row=0, column=j + 1, padx=2, pady=2)

        for i in range(self.n):

            ctk.CTkLabel(
                self, text=self.labels[i][:16],
                font=ctk.CTkFont(size=11, weight="bold"),
                width=LABEL_W, anchor="e"
            ).grid(row=i + 1, column=0, padx=(4, 2), pady=2)

            for j in range(self.n):
                if i == j:

                    ctk.CTkLabel(
                        self, text="1",
                        width=CELL_W, height=CELL_H,
                        fg_color="#2b2b2b", corner_radius=4, anchor="center"
                    ).grid(row=i + 1, column=j + 1, padx=2, pady=2)

                elif i < j:

                    entry = ctk.CTkEntry(
                        self,
                        width=CELL_W, height=CELL_H,
                        justify="center",
                        placeholder_text="1",
                        fg_color="#16213e",
                        border_color="#457b9d",
                        font=ctk.CTkFont(size=12)
                    )
                    entry.insert(0, "1")
                    entry.grid(row=i + 1, column=j + 1, padx=2, pady=2)

                    entry.bind("<FocusOut>", lambda e, _i=i, _j=j: self._on_entry_change(_i, _j))
                    entry.bind("<Return>",   lambda e, _i=i, _j=j: self._on_entry_change(_i, _j))
                    self._entries[(i, j)] = entry

                else:

                    lbl_w = ctk.CTkLabel(
                        self, text="1",
                        width=CELL_W, height=CELL_H,
                        fg_color="#0d1b2a", corner_radius=4,
                        text_color="#a8dadc", anchor="center",
                        font=ctk.CTkFont(size=11)
                    )
                    lbl_w.grid(row=i + 1, column=j + 1, padx=2, pady=2)
                    self._recip_labels[(i, j)] = lbl_w

    def _on_entry_change(self, i: int, j: int):

        entry = self._entries.get((i, j))
        if entry is None:
            return
        raw = entry.get()
        val = parse_value(raw, fallback=1.0)


        entry.delete(0, "end")
        if "/" in raw and val != 1.0:
            entry.insert(0, raw.strip())   
        else:
            entry.insert(0, str(round(val, 4)).rstrip("0").rstrip(".") if val != int(val) else str(int(val)))


        recip_lbl = self._recip_labels.get((j, i))
        if recip_lbl:
            recip_lbl.configure(text=format_reciprocal(val))

        if self.on_change:
            self.on_change(i, j, val)

    def get_matrix(self) -> np.ndarray:

        mat = np.ones((self.n, self.n))
        for (i, j), entry in self._entries.items():
            val = parse_value(entry.get(), 1.0)
            mat[i][j] = val
            mat[j][i] = 1.0 / val if val != 0 else 1.0
        return mat



class AlternativeScoringTable(ctk.CTkFrame):

    def __init__(self, parent, alternatives: List[str], criteria: List[str], **kwargs):
        super().__init__(parent, **kwargs)
        self.alternatives = alternatives
        self.criteria     = criteria
        self.n_alt        = len(alternatives)
        self.n_crit       = len(criteria)
        self._entries: Dict[tuple, ctk.CTkEntry] = {}
        self._build()

    def _build(self):
        # Legend
        legend = ctk.CTkFrame(self, fg_color="#0d1b2a")
        legend.grid(row=0, column=0, columnspan=self.n_crit + 1,
                    sticky="ew", padx=4, pady=(4, 10))
        ctk.CTkLabel(
            legend,
            text="Enter scores 1–9  (1 = weakest  ·  9 = strongest  ·  decimals allowed e.g. 7.5)",
            font=ctk.CTkFont(size=11), text_color="#a8dadc"
        ).pack(padx=10, pady=5)

  
        ctk.CTkLabel(
            self, text="Alternative",
            width=LABEL_W, font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#1d3557", corner_radius=4, anchor="center"
        ).grid(row=1, column=0, padx=3, pady=3, sticky="ew")


        for j, crit in enumerate(self.criteria):
            ctk.CTkLabel(
                self, text=crit[:16],
                font=ctk.CTkFont(size=11, weight="bold"),
                width=CELL_W + 10, fg_color="#1d3557", corner_radius=4,
                anchor="center", wraplength=CELL_W + 4
            ).grid(row=1, column=j + 1, padx=3, pady=3, sticky="ew")


        for i, alt in enumerate(self.alternatives):
            row_fg = "#16213e" if i % 2 == 0 else "#0d1b2a"

            ctk.CTkLabel(
                self, text=alt[:18],
                font=ctk.CTkFont(size=12, weight="bold"),
                width=LABEL_W, fg_color=row_fg,
                corner_radius=4, anchor="w"
            ).grid(row=i + 2, column=0, padx=3, pady=3, sticky="ew")

            for j in range(self.n_crit):
                entry = ctk.CTkEntry(
                    self,
                    width=CELL_W + 10, height=CELL_H + 2,
                    justify="center",
                    placeholder_text="1",
                    fg_color=row_fg,
                    border_color="#457b9d",
                    font=ctk.CTkFont(size=13, weight="bold")
                )
                entry.insert(0, "1")
                entry.grid(row=i + 2, column=j + 1, padx=3, pady=3)
                # Highlight on bad input
                entry.bind("<FocusOut>", lambda e, _e=entry: self._validate_cell(_e))
                self._entries[(i, j)] = entry

    def _validate_cell(self, entry: ctk.CTkEntry):

        raw = entry.get()
        val = parse_value(raw, fallback=1.0)
        val = max(1.0, min(9.0, val))   # score table: clamp strictly to 1-9
        entry.delete(0, "end")
        entry.insert(0, str(round(val, 2)).rstrip("0").rstrip(".") if val != int(val) else str(int(val)))

    def get_scores(self) -> np.ndarray:

        scores = np.ones((self.n_alt, self.n_crit))
        for (i, j), entry in self._entries.items():
            scores[i][j] = parse_value(entry.get(), 1.0)
        return scores

    def get_pairwise_matrices(self) -> Dict[str, np.ndarray]:

        scores = self.get_scores()
        return {
            crit: scores_to_pairwise(scores[:, j])
            for j, crit in enumerate(self.criteria)
        }



class MatrixView(ctk.CTkFrame):

    def __init__(self, parent, viewmodel, on_next: Callable, on_back: Callable, **kwargs):
        super().__init__(parent, **kwargs)
        self.vm             = viewmodel
        self.on_next        = on_next
        self.on_back        = on_back
        self.scoring_table:  AlternativeScoringTable  = None
        self.criteria_widget: CriteriaPairwiseWidget  = None

    def refresh(self):
        for w in self.winfo_children():
            w.destroy()
        self.scoring_table   = None
        self.criteria_widget = None
        self._build_ui()

    def _build_ui(self):
        criteria     = self.vm.get_criteria()
        alternatives = self.vm.get_alternatives()

        # Header
        ctk.CTkLabel(
            self, text="⚖️  Comparison & Scoring",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=(18, 2))
        ctk.CTkLabel(
            self,
            text="A · Rate criteria importance  •  B · Score each alternative per criterion",
            font=ctk.CTkFont(size=12), text_color="gray"
        ).pack(pady=(0, 8))

        scroll = ctk.CTkScrollableFrame(self)
        scroll.pack(fill="both", expand=True, padx=20, pady=4)


        sec_a = ctk.CTkFrame(scroll, fg_color="#16213e", corner_radius=10)
        sec_a.pack(fill="x", padx=6, pady=(6, 14))

        ctk.CTkLabel(
            sec_a,
            text="A  ·  Criteria Importance  (pairwise — enter values like 3, 1/3, 5, 0.5 …)",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="#e9c46a"
        ).pack(anchor="w", padx=14, pady=(10, 2))
        ctk.CTkLabel(
            sec_a,
            text="How much more important is the row criterion vs the column criterion?  "
                 "Use 1=equal · 3=moderate · 5=strong · 7=very strong · 9=extreme  (1/x for inverse)",
            font=ctk.CTkFont(size=11), text_color="gray", wraplength=900
        ).pack(anchor="w", padx=14, pady=(0, 8))

        self.criteria_widget = CriteriaPairwiseWidget(
            sec_a, criteria,
            on_change=lambda i, j, v: self.vm.update_criteria_matrix(i, j, v),
            fg_color="transparent"
        )
        self.criteria_widget.pack(padx=14, pady=(0, 14))


        sec_b = ctk.CTkFrame(scroll, fg_color="#0d1b2a", corner_radius=10)
        sec_b.pack(fill="x", padx=6, pady=(0, 10))

        ctk.CTkLabel(
            sec_b,
            text="B  ·  Alternative Scores  (rate each alternative per criterion, 1–9)",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="#e9c46a"
        ).pack(anchor="w", padx=14, pady=(10, 2))
        ctk.CTkLabel(
            sec_b,
            text="How well does each alternative satisfy each criterion?  1 = worst  ·  9 = best",
            font=ctk.CTkFont(size=11), text_color="gray"
        ).pack(anchor="w", padx=14, pady=(0, 8))

        self.scoring_table = AlternativeScoringTable(
            sec_b, alternatives, criteria,
            fg_color="transparent"
        )
        self.scoring_table.pack(padx=14, pady=(0, 14))


        nav = ctk.CTkFrame(self, fg_color="transparent")
        nav.pack(pady=14)
        ctk.CTkButton(
            nav, text="← Back", command=self.on_back,
            width=120, fg_color="#555", hover_color="#777"
        ).pack(side="left", padx=10)
        ctk.CTkButton(
            nav, text="▶  Calculate AHP",
            command=self._handle_calculate,
            height=44, font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#e76f51", hover_color="#f4a261"
        ).pack(side="left", padx=10)

    def _handle_calculate(self):

        criteria     = self.vm.get_criteria()
        alternatives = self.vm.get_alternatives()

        # Push criteria pairwise matrix
        if self.criteria_widget:
            mat = self.criteria_widget.get_matrix()
            for i in range(len(criteria)):
                for j in range(i + 1, len(criteria)):
                    self.vm.update_criteria_matrix(i, j, mat[i][j])

        # Derive and push alternative pairwise matrices
        if self.scoring_table:
            for crit, mat in self.scoring_table.get_pairwise_matrices().items():
                n = len(alternatives)
                for i in range(n):
                    for j in range(i + 1, n):
                        self.vm.update_alt_matrix(crit, i, j, mat[i][j])

        self.on_next()
