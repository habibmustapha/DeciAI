import customtkinter as ctk
import numpy as np
import threading
from typing import List, Callable, Dict
from itertools import combinations



def parse_float(text: str, fallback: float = 0.0) -> float:
    try:
        return float(text.strip().replace(",", "."))
    except ValueError:
        return fallback


def parse_pairwise(text: str, fallback: float = 1.0) -> float:
    text = text.strip().replace(",", ".")
    try:
        if "/" in text:
            a, b = text.split("/")
            return float(a) / float(b)
        return float(text)
    except (ValueError, ZeroDivisionError):
        return fallback


def fmt_val(val: float) -> str:

    if val <= 0:
        return "1"
    if val < 1:
        denom = round(1 / val)
        return f"1/{denom}"
    if val == int(val):
        return str(int(val))
    return f"{val:.3f}"


def raw_scores_to_pairwise(col: np.ndarray, higher_is_better: bool = True) -> np.ndarray:
    n = len(col)
    mat = np.ones((n, n))
    for i in range(n):
        for j in range(n):
            d = col[j] if col[j] != 0 else 1e-9
            u = col[i] if col[i] != 0 else 1e-9
            mat[i][j] = (u / d) if higher_is_better else (d / u)
    return np.clip(mat, 1/9, 9)


EVEN_CLR   = "#16213e"
ODD_CLR    = "#0d1b2a"
HEADER_CLR = "#1d3557"
CELL_W     = 110
ROW_LBL_W  = 100
CELL_H     = 34

SCALE_HINT = (
    "1 = equal  ·  3 = moderate  ·  5 = strong  ·  7 = very strong  ·  9 = extreme  "
    "·  use 1/3, 1/5 … for inverse"
)




class PairQuestionRow(ctk.CTkFrame):

    def __init__(self, parent, label_a: str, label_b: str,
                 verb: str = "more important",
                 bg: str = EVEN_CLR,
                 on_change: Callable = None,
                 **kwargs):
        super().__init__(parent, fg_color=bg, corner_radius=6, **kwargs)
        self.on_change = on_change
        self._val = 1.0

        ctk.CTkLabel(self, text="How much  ", font=ctk.CTkFont(size=12),
                     text_color="gray").pack(side="left", padx=(12, 0), pady=10)

        ctk.CTkLabel(self, text=label_a, font=ctk.CTkFont(size=12, weight="bold"),
                     text_color="#e9c46a").pack(side="left", pady=10)

        ctk.CTkLabel(self, text=f"  is {verb} than  ",
                     font=ctk.CTkFont(size=12), text_color="gray").pack(side="left", pady=10)

        ctk.CTkLabel(self, text=label_b, font=ctk.CTkFont(size=12, weight="bold"),
                     text_color="#a8dadc").pack(side="left", pady=10)

        ctk.CTkLabel(self, text="  ?", font=ctk.CTkFont(size=12),
                     text_color="gray").pack(side="left", pady=10)

        self.entry = ctk.CTkEntry(
            self, width=90, height=34, justify="center",
            placeholder_text="1",
            fg_color="#1a1a2e", border_color="#457b9d",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.entry.insert(0, "1")
        self.entry.pack(side="right", padx=12, pady=8)
        self.entry.bind("<FocusOut>", self._commit)
        self.entry.bind("<Return>",   self._commit)

    def _commit(self, _event=None):
        v = parse_pairwise(self.entry.get(), 1.0)
        v = max(1/9, min(9.0, v))
        self._val = v
        self.entry.delete(0, "end")
        self.entry.insert(0, fmt_val(v))
        if self.on_change:
            self.on_change(v)

    def get_value(self) -> float:
        return parse_pairwise(self.entry.get(), 1.0)



class RawDataTable(ctk.CTkFrame):
    def __init__(self, parent, alternatives: List[str], criteria: List[str], **kwargs):
        super().__init__(parent, **kwargs)
        self.alternatives = alternatives
        self.criteria     = criteria
        self.n_alt        = len(alternatives)
        self.n_crit       = len(criteria)
        self._entries: Dict[tuple, ctk.CTkEntry] = {}
        self._higher_is_better: Dict[int, bool]  = {j: True for j in range(self.n_crit)}
        self._dir_btns: Dict[int, ctk.CTkButton] = {}
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="", width=ROW_LBL_W, height=36
                     ).grid(row=0, column=0, padx=2, pady=2)
        for j, crit in enumerate(self.criteria):
            ctk.CTkLabel(
                self, text=crit,
                font=ctk.CTkFont(size=11, weight="bold"),
                width=CELL_W, height=36, fg_color=HEADER_CLR,
                corner_radius=4, anchor="center", wraplength=CELL_W - 8
            ).grid(row=0, column=j+1, padx=2, pady=2, sticky="ew")

        ctk.CTkLabel(self, text="Direction", width=ROW_LBL_W, height=26,
                     font=ctk.CTkFont(size=10), text_color="gray"
                     ).grid(row=1, column=0, padx=2, pady=1)
        for j in range(self.n_crit):
            btn = ctk.CTkButton(
                self, text="↑ Higher = Better", width=CELL_W, height=26,
                font=ctk.CTkFont(size=10), fg_color="#2d6a4f", hover_color="#1b4332",
                command=lambda _j=j: self._toggle(_j)
            )
            btn.grid(row=1, column=j+1, padx=2, pady=1)
            self._dir_btns[j] = btn

        ctk.CTkLabel(self, text="", height=4).grid(row=2, column=0, columnspan=self.n_crit+1)

        for i, alt in enumerate(self.alternatives):
            bg = EVEN_CLR if i % 2 == 0 else ODD_CLR
            ctk.CTkLabel(
                self, text=alt, font=ctk.CTkFont(size=12, weight="bold"),
                width=ROW_LBL_W, height=CELL_H, fg_color=bg,
                corner_radius=4, anchor="center"
            ).grid(row=i+3, column=0, padx=2, pady=2, sticky="ew")
            for j in range(self.n_crit):
                e = ctk.CTkEntry(
                    self, width=CELL_W, height=CELL_H, justify="center",
                    placeholder_text="0", fg_color=bg,
                    border_color="#457b9d", font=ctk.CTkFont(size=12)
                )
                e.grid(row=i+3, column=j+1, padx=2, pady=2)
                self._entries[(i, j)] = e

    def _toggle(self, j):
        self._higher_is_better[j] = not self._higher_is_better[j]
        if self._higher_is_better[j]:
            self._dir_btns[j].configure(text="↑ Higher = Better",
                                         fg_color="#2d6a4f", hover_color="#1b4332")
        else:
            self._dir_btns[j].configure(text="↓ Lower = Better",
                                         fg_color="#7b2d8b", hover_color="#4a0e8f")

    def get_raw_matrix(self) -> np.ndarray:
        mat = np.zeros((self.n_alt, self.n_crit))
        for (i, j), e in self._entries.items():
            mat[i][j] = parse_float(e.get(), 0.0)
        return mat

    def get_pairwise_matrices(self) -> Dict[str, np.ndarray]:
        raw = self.get_raw_matrix()
        result = {}
        for j, crit in enumerate(self.criteria):
            col = raw[:, j]
            result[crit] = (np.ones((self.n_alt, self.n_alt))
                            if col.sum() == 0
                            else raw_scores_to_pairwise(col, self._higher_is_better[j]))
        return result

    def has_data(self) -> bool:
        return self.get_raw_matrix().sum() > 0




class CriteriaQuestionsWidget(ctk.CTkFrame):

    def __init__(self, parent, criteria: List[str],
                 on_change: Callable = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.criteria  = criteria
        self.on_change = on_change
        self.pairs     = list(combinations(range(len(criteria)), 2))
        self._rows: Dict[tuple, PairQuestionRow] = {}
        self._cr_lbl: ctk.CTkLabel = None
        self._build()

    def _build(self):
        ctk.CTkLabel(
            self, text=SCALE_HINT,
            font=ctk.CTkFont(size=11), text_color="#a8dadc",
            fg_color="#0d1b2a", corner_radius=6, wraplength=860
        ).pack(fill="x", pady=(0, 10), ipadx=10, ipady=6)

        for idx, (i, j) in enumerate(self.pairs):
            row = PairQuestionRow(
                self,
                label_a=self.criteria[i],
                label_b=self.criteria[j],
                verb="more important",
                bg=EVEN_CLR if idx % 2 == 0 else ODD_CLR,
                on_change=lambda v, _i=i, _j=j: self._changed(_i, _j, v)
            )
            row.pack(fill="x", pady=3)
            self._rows[(i, j)] = row

        self._cr_lbl = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=12, weight="bold")
        )
        self._cr_lbl.pack(anchor="e", padx=8, pady=(6, 0))

    def _changed(self, i, j, v):
        if self.on_change:
            self.on_change(i, j, v)
        self._refresh_cr()

    def _refresh_cr(self):
        from services.consistency import ConsistencyChecker
        from services.ahp_engine  import AHPEngine
        mat = self.get_matrix()
        try:
            _, pv   = AHPEngine().normalize_matrix(mat)
            ci, cr, _ = ConsistencyChecker().compute_cr(mat, pv)
            if cr <= 0.10:
                self._cr_lbl.configure(
                    text=f"✓  CR = {cr:.4f}  (consistent)", text_color="#2d6a4f")
            else:
                self._cr_lbl.configure(
                    text=f"⚠  CR = {cr:.4f}  — inconsistent (target ≤ 0.10)",
                    text_color="#e63946")
        except Exception:
            pass

    def get_matrix(self) -> np.ndarray:
        n = len(self.criteria)
        mat = np.ones((n, n))
        for (i, j), row in self._rows.items():
            v = row.get_value()
            mat[i][j] = v
            mat[j][i] = 1.0 / v if v else 1.0
        return mat

    def get_questions_with_values(self) -> List[dict]:
        return [
            {"a": self.criteria[i], "b": self.criteria[j], "value": row.get_value()}
            for (i, j), row in self._rows.items()
        ]

    def get_cr(self):
        from services.consistency import ConsistencyChecker
        from services.ahp_engine  import AHPEngine
        mat = self.get_matrix()
        _, pv = AHPEngine().normalize_matrix(mat)
        ci, cr, _ = ConsistencyChecker().compute_cr(mat, pv)
        return ci, cr



class AlternativeQuestionsWidget(ctk.CTkFrame):

    def __init__(self, parent, criteria: List[str], alternatives: List[str],
                 on_change: Callable = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.criteria     = criteria
        self.alternatives = alternatives
        self.on_change    = on_change
        self.pairs        = list(combinations(range(len(alternatives)), 2))

        self._rows: Dict[tuple, PairQuestionRow] = {}
        self._cr_labels: Dict[str, ctk.CTkLabel] = {}
        self._build()

    def _build(self):
        ctk.CTkLabel(
            self, text=SCALE_HINT,
            font=ctk.CTkFont(size=11), text_color="#a8dadc",
            fg_color="#0d1b2a", corner_radius=6, wraplength=860
        ).pack(fill="x", pady=(0, 10), ipadx=10, ipady=6)

        tabs = ctk.CTkTabview(self)
        tabs.pack(fill="x")

        for crit in self.criteria:
            tabs.add(crit[:20])
            tab = tabs.tab(crit[:20])

            scroll = ctk.CTkScrollableFrame(tab, height=280)
            scroll.pack(fill="both", expand=True)

            for idx, (i, j) in enumerate(self.pairs):
                row = PairQuestionRow(
                    scroll,
                    label_a=self.alternatives[i],
                    label_b=self.alternatives[j],
                    verb=f"better for  \"{crit}\"",
                    bg=EVEN_CLR if idx % 2 == 0 else ODD_CLR,
                    on_change=lambda v, _c=crit, _i=i, _j=j: self._changed(_c, _i, _j, v)
                )
                row.pack(fill="x", pady=2)
                self._rows[(crit, i, j)] = row


            cr_lbl = ctk.CTkLabel(scroll, text="", font=ctk.CTkFont(size=12, weight="bold"))
            cr_lbl.pack(anchor="e", padx=8, pady=(6, 2))
            self._cr_labels[crit] = cr_lbl

    def _changed(self, crit, i, j, v):
        if self.on_change:
            self.on_change(crit, i, j, v)
        self._refresh_cr(crit)

    def _refresh_cr(self, crit: str):
        from services.consistency import ConsistencyChecker
        from services.ahp_engine  import AHPEngine
        mat = self.get_matrix(crit)
        try:
            _, pv     = AHPEngine().normalize_matrix(mat)
            ci, cr, _ = ConsistencyChecker().compute_cr(mat, pv)
            lbl = self._cr_labels.get(crit)
            if lbl:
                if cr <= 0.10:
                    lbl.configure(text=f"✓  CR = {cr:.4f}", text_color="#2d6a4f")
                else:
                    lbl.configure(
                        text=f"⚠  CR = {cr:.4f}  — inconsistent",
                        text_color="#e63946")
        except Exception:
            pass

    def get_matrix(self, crit: str) -> np.ndarray:
        n = len(self.alternatives)
        mat = np.ones((n, n))
        for (c, i, j), row in self._rows.items():
            if c == crit:
                v = row.get_value()
                mat[i][j] = v
                mat[j][i] = 1.0 / v if v else 1.0
        return mat

    def get_all_matrices(self) -> Dict[str, np.ndarray]:
        return {crit: self.get_matrix(crit) for crit in self.criteria}



class DataInputView(ctk.CTkFrame):

    def __init__(self, parent, viewmodel, on_next: Callable, on_back: Callable, **kwargs):
        super().__init__(parent, **kwargs)
        self.vm      = viewmodel
        self.on_next = on_next
        self.on_back = on_back
        self.data_table:       RawDataTable            = None
        self.crit_questions:   CriteriaQuestionsWidget = None
        self._verdict_lbl:     ctk.CTkLabel            = None
        self._verify_btn:      ctk.CTkButton           = None

    def refresh(self, pdf_matrix=None):
        for w in self.winfo_children():
            w.destroy()
        self.data_table     = None
        self.crit_questions = None
        self._verdict_lbl   = None
        self._verify_btn    = None
        self._build_ui()

        if pdf_matrix is not None:
            self._prefill_table(pdf_matrix)

    def _build_ui(self):
        criteria     = self.vm.get_criteria()
        alternatives = self.vm.get_alternatives()

        ctk.CTkLabel(self, text="📊  Enter Decision Data",
                     font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(16, 2))
        ctk.CTkLabel(self, text=f"Goal: {self.vm.get_goal()}",
                     font=ctk.CTkFont(size=12), text_color="#a8dadc").pack(pady=(0, 8))

        scroll = ctk.CTkScrollableFrame(self)
        scroll.pack(fill="both", expand=True, padx=20, pady=4)

       
        self._section(scroll, "A  ·  Raw Data Table",
                      "Fill in the actual measured/observed values. "
                      "Use ↑/↓ to set whether higher or lower is better per criterion.")

        self.data_table = RawDataTable(
            scroll, alternatives, criteria, fg_color=ODD_CLR
        )
        self.data_table.pack(padx=14, pady=(0, 14))

       
        self._section(scroll, "B  ·  Criteria Importance",
                      "For each pair of criteria, say how much more important the first is than the second.")

        self.crit_questions = CriteriaQuestionsWidget(
            scroll, criteria,
            on_change=lambda i, j, v: self.vm.update_criteria_matrix(i, j, v),
            fg_color="transparent"
        )
        self.crit_questions.pack(fill="x", padx=14, pady=(0, 8))

        # LLM verify row
        vrow = ctk.CTkFrame(scroll, fg_color="transparent")
        vrow.pack(fill="x", padx=14, pady=(0, 6))

        self._verify_btn = ctk.CTkButton(
            vrow, text="🤖  Ask Mistral to Verify Consistency",
            width=300, height=34, font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#4a0e8f", hover_color="#7b2d8b",
            command=self._verify_consistency
        )
        self._verify_btn.pack(side="left", padx=(0, 10))
        ctk.CTkLabel(vrow, text="Mistral reviews your answers and flags contradictions.",
                     font=ctk.CTkFont(size=11), text_color="gray").pack(side="left")


        self._verdict_lbl = ctk.CTkLabel(
            scroll, text="",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )


        nav = ctk.CTkFrame(self, fg_color="transparent")
        nav.pack(pady=14)
        ctk.CTkButton(nav, text="← Back", command=self.on_back,
                      width=120, fg_color="#555", hover_color="#777"
                      ).pack(side="left", padx=10)
        self.error_lbl = ctk.CTkLabel(nav, text="", text_color="#e63946",
                                       font=ctk.CTkFont(size=12))
        self.error_lbl.pack(side="left", padx=10)
        ctk.CTkButton(nav, text="▶  Run AHP Analysis",
                      command=self._handle_calculate, height=44,
                      font=ctk.CTkFont(size=15, weight="bold"),
                      fg_color="#e76f51", hover_color="#f4a261"
                      ).pack(side="left", padx=10)




    def _prefill_table(self, matrix):

        if self.data_table is None:
            return
        import numpy as np
        n_alt, n_crit = matrix.shape
        for i in range(min(n_alt, self.data_table.n_alt)):
            for j in range(min(n_crit, self.data_table.n_crit)):
                entry = self.data_table._entries.get((i, j))
                if entry is not None:
                    val = float(matrix[i][j])
                    entry.delete(0, "end")
                    entry.insert(0, str(int(val)) if val == int(val) else f"{val:.3f}")

    def _section(self, parent, title: str, subtitle: str):
        ctk.CTkLabel(parent, text=title,
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="#e9c46a").pack(anchor="w", padx=14, pady=(18, 2))
        ctk.CTkLabel(parent, text=subtitle,
                     font=ctk.CTkFont(size=11), text_color="gray",
                     wraplength=900).pack(anchor="w", padx=14, pady=(0, 8))



    def _verify_consistency(self):

        ci, cr = self.crit_questions.get_cr()
        questions = self.crit_questions.get_questions_with_values()


        self._verify_btn.configure(state="disabled", text="Checking…")
        self._verdict_lbl.configure(text="⏳  Asking Mistral…", text_color="#a8dadc")
        self._verdict_lbl.pack(anchor="w", padx=14, pady=(0, 8))

        def task():
            verdict = self.vm.llm.verify_criteria_consistency(
                goal=self.vm.get_goal(),
                criteria=self.vm.get_criteria(),
                questions=questions, cr=cr, ci=ci
            )
            # Clean the verdict to one line
            line = verdict.strip().splitlines()[0] if verdict.strip() else verdict.strip()
            consistent = cr <= 0.10
            color = "#2d6a4f" if consistent else "#e63946"

            def _ui():
                self._verdict_lbl.configure(text=line, text_color=color)
                self._verify_btn.configure(
                    state="normal", text="🤖  Ask Mistral to Verify Consistency")

            self.after(0, _ui)

        threading.Thread(target=task, daemon=True).start()



    def _handle_calculate(self):
        if not self.data_table.has_data():
            self.error_lbl.configure(text="⚠ Please fill in the data table first.")
            return
        self.error_lbl.configure(text="")

        criteria     = self.vm.get_criteria()
        alternatives = self.vm.get_alternatives()


        cmat = self.crit_questions.get_matrix()
        for i in range(len(criteria)):
            for j in range(i+1, len(criteria)):
                self.vm.update_criteria_matrix(i, j, cmat[i][j])


        for crit, mat in self.data_table.get_pairwise_matrices().items():
            n = len(alternatives)
            for i in range(n):
                for j in range(i+1, n):
                    self.vm.update_alt_matrix(crit, i, j, mat[i][j])

        self.vm.set_raw_data(
            self.data_table.get_raw_matrix(),
            self.data_table._higher_is_better.copy()
        )

        self.on_next()
