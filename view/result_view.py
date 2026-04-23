import customtkinter as ctk
import numpy as np
from typing import Callable, Dict, List



class MatrixTable(ctk.CTkFrame):

    def __init__(self, parent, matrix: np.ndarray, row_labels: List[str],
                 col_labels: List[str] = None, title: str = "", **kwargs):
        super().__init__(parent, **kwargs)
        if col_labels is None:
            col_labels = row_labels
        self._build(matrix, row_labels, col_labels, title)

    def _build(self, matrix, row_labels, col_labels, title):
        if title:
            ctk.CTkLabel(
                self, text=title,
                font=ctk.CTkFont(size=12, weight="bold"), text_color="#a8dadc"
            ).grid(row=0, column=0, columnspan=len(col_labels) + 1,
                   padx=6, pady=(6, 2), sticky="w")


        for j, lbl in enumerate(col_labels):
            ctk.CTkLabel(
                self, text=lbl[:10],
                font=ctk.CTkFont(size=10, weight="bold"),
                width=70, fg_color="#1d3557", corner_radius=3
            ).grid(row=1, column=j + 1, padx=1, pady=1)


        for i, rlbl in enumerate(row_labels):
            ctk.CTkLabel(
                self, text=rlbl[:12],
                font=ctk.CTkFont(size=10, weight="bold"),
                width=90, anchor="e"
            ).grid(row=i + 2, column=0, padx=(4, 2), pady=1)

            for j in range(len(col_labels)):
                val = matrix[i][j]
                color = "#0d1b2a" if (i + j) % 2 == 0 else "#16213e"
                ctk.CTkLabel(
                    self, text=f"{val:.4f}",
                    font=ctk.CTkFont(size=10),
                    width=70, fg_color=color, corner_radius=2, anchor="center"
                ).grid(row=i + 2, column=j + 1, padx=1, pady=1)



class ResultView(ctk.CTkFrame):

    def __init__(self, parent, viewmodel, on_restart: Callable, **kwargs):
        super().__init__(parent, **kwargs)
        self.vm = viewmodel
        self.on_restart = on_restart
        self.explanation_text = ""
        self._setup_callbacks()

    def _setup_callbacks(self):
        self.vm.on_explanation_token = self._append_explanation_token
        self.vm.on_explanation_complete = self._on_explanation_done

    def refresh(self):

        for widget in self.winfo_children():
            widget.destroy()
        self._build_ui()

    def _build_ui(self):
        results = self.vm.get_results()
        if not results:
            ctk.CTkLabel(self, text="No results yet.").pack(pady=40)
            return


        ctk.CTkLabel(
            self, text="AHP Results",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=(16, 4))

        ctk.CTkLabel(
            self, text=f"Goal: {self.vm.get_goal()}",
            font=ctk.CTkFont(size=13), text_color="#a8dadc"
        ).pack(pady=(0, 8))


        scroll = ctk.CTkScrollableFrame(self)
        scroll.pack(fill="both", expand=True, padx=20, pady=5)

        self._build_raw_data_section(scroll, results)
        self._build_ranking_section(scroll, results)
        self._build_consistency_section(scroll, results)
        self._build_matrices_section(scroll, results)
        self._build_explanation_section(scroll)
        self._build_action_buttons()

    def _build_raw_data_section(self, parent, results):

        raw = self.vm.get_raw_data()
        if raw is None:
            return

        criteria     = results["criteria"]
        alternatives = results["alternatives"]
        directions   = self.vm.get_direction_flags()

        ctk.CTkLabel(
            parent, text="📋  Input Data Table",
            font=ctk.CTkFont(size=16, weight="bold"), text_color="#e9c46a"
        ).pack(anchor="w", pady=(12, 4), padx=10)

        tbl_frame = ctk.CTkFrame(parent, fg_color="#16213e", corner_radius=8)
        tbl_frame.pack(fill="x", padx=10, pady=(0, 14))

        CELL_W   = 110
        LABEL_W  = 100
        HDR_CLR  = "#1d3557"
        EVEN_CLR = "#16213e"
        ODD_CLR  = "#0d1b2a"

        inner = ctk.CTkFrame(tbl_frame, fg_color="transparent")
        inner.pack(padx=10, pady=10)

        ctk.CTkLabel(inner, text="", width=LABEL_W, height=32).grid(row=0, column=0, padx=2, pady=2)

        for j, crit in enumerate(criteria):
            dir_sym = "up" if directions.get(j, True) else "down"
            ctk.CTkLabel(
                inner, text=f"{crit} ({dir_sym})",
                font=ctk.CTkFont(size=10, weight="bold"),
                width=CELL_W, height=36,
                fg_color=HDR_CLR, corner_radius=4,
                anchor="center", wraplength=CELL_W - 8
            ).grid(row=0, column=j + 1, padx=2, pady=2)

        for i, alt in enumerate(alternatives):
            row_fg = EVEN_CLR if i % 2 == 0 else ODD_CLR
            ctk.CTkLabel(
                inner, text=alt,
                font=ctk.CTkFont(size=11, weight="bold"),
                width=LABEL_W, height=32,
                fg_color=row_fg, corner_radius=4, anchor="center"
            ).grid(row=i + 1, column=0, padx=2, pady=2)

            for j in range(len(criteria)):
                val = raw[i][j]
                val_str = str(int(val)) if val == int(val) else f"{val:.3f}"
                ctk.CTkLabel(
                    inner, text=val_str,
                    font=ctk.CTkFont(size=11),
                    width=CELL_W, height=32,
                    fg_color=row_fg, corner_radius=3, anchor="center"
                ).grid(row=i + 1, column=j + 1, padx=2, pady=2)


    def _build_ranking_section(self, parent, results):
        ctk.CTkLabel(
            parent, text="🏆  Final Ranking",
            font=ctk.CTkFont(size=16, weight="bold"), text_color="#e9c46a"
        ).pack(anchor="w", pady=(12, 6), padx=10)

        criteria = results["criteria"]
        crit_pv = results["criteria_priority_vector"]

        for rank, name, score in results["ranking"]:
            row_frame = ctk.CTkFrame(parent, fg_color="#16213e", corner_radius=8)
            row_frame.pack(fill="x", padx=10, pady=3)



            medal = medals.get(rank, f"#{rank}")
            ctk.CTkLabel(
                row_frame, text=medal,
                font=ctk.CTkFont(size=20), width=50
            ).pack(side="left", padx=10, pady=8)

            ctk.CTkLabel(
                row_frame, text=name,
                font=ctk.CTkFont(size=14, weight="bold"),
                width=200, anchor="w"
            ).pack(side="left", padx=4)


            bar_container = ctk.CTkFrame(row_frame, fg_color="transparent")
            bar_container.pack(side="left", fill="x", expand=True, padx=10)

            max_score = max(s for _, _, s in results["ranking"])
            pct = score / max_score if max_score > 0 else 0
            bar = ctk.CTkProgressBar(bar_container, width=250, height=16)
            bar.pack(side="left", padx=4, pady=10)
            bar.set(pct)

            ctk.CTkLabel(
                row_frame, text=f"{score:.4f}",
                font=ctk.CTkFont(size=13, weight="bold"), text_color="#e9c46a",
                width=70
            ).pack(side="right", padx=12)


        ctk.CTkLabel(
            parent, text="  Criteria Weights",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="#e9c46a"
        ).pack(anchor="w", pady=(16, 4), padx=10)

        weights_frame = ctk.CTkFrame(parent, fg_color="#0d1b2a")
        weights_frame.pack(fill="x", padx=10, pady=4)

        for i, (crit, weight) in enumerate(zip(criteria, crit_pv)):
            row = ctk.CTkFrame(weights_frame, fg_color="transparent")
            row.pack(fill="x", padx=8, pady=2)
            ctk.CTkLabel(row, text=crit, width=200, anchor="w").pack(side="left")
            bar = ctk.CTkProgressBar(row, width=200, height=12)
            bar.pack(side="left", padx=8, pady=4)
            bar.set(float(weight))
            ctk.CTkLabel(row, text=f"{weight:.4f}", text_color="#a8dadc").pack(side="left")

    def _build_consistency_section(self, parent, results):
        ctk.CTkLabel(
            parent, text="🔍  Consistency Analysis",
            font=ctk.CTkFont(size=16, weight="bold"), text_color="#e9c46a"
        ).pack(anchor="w", pady=(16, 6), padx=10)

        def cr_row(frame, label, cr_data):
            row = ctk.CTkFrame(frame, fg_color="transparent")
            row.pack(fill="x", padx=8, pady=2)
            ci = cr_data.get("CI", 0)
            cr = cr_data.get("CR", 0)
            lmax = cr_data.get("lambda_max", 0)
            ok = cr <= 0.1
            color = "#2d6a4f" if ok else "#9b2335"
            status = "✓ Consistent" if ok else "⚠ Inconsistent (CR > 0.1)"
            ctk.CTkLabel(row, text=label, width=200, anchor="w").pack(side="left")
            ctk.CTkLabel(
                row, text=f"CI={ci:.4f}  CR={cr:.4f}  λmax={lmax:.4f}",
                text_color="#a8dadc", width=300
            ).pack(side="left")
            ctk.CTkLabel(row, text=status, text_color=color).pack(side="left", padx=8)

        consist_frame = ctk.CTkFrame(parent, fg_color="#16213e")
        consist_frame.pack(fill="x", padx=10, pady=4)

        
        if results.get("criteria_consistency"):
            cr_row(consist_frame, "Criteria Matrix", results["criteria_consistency"])


        for crit, cr_data in results.get("alt_consistencies", {}).items():
            cr_row(consist_frame, f"  Alt/{crit[:20]}", cr_data)

    def _build_matrices_section(self, parent, results):
        ctk.CTkLabel(
            parent, text="📐  Matrix Details",
            font=ctk.CTkFont(size=16, weight="bold"), text_color="#e9c46a"
        ).pack(anchor="w", pady=(16, 6), padx=10)

        criteria = results["criteria"]
        alternatives = results["alternatives"]


        tabview = ctk.CTkTabview(parent)
        tabview.pack(fill="x", padx=10, pady=4)


        tabview.add("Criteria")
        crit_scroll = ctk.CTkScrollableFrame(tabview.tab("Criteria"), height=300)
        crit_scroll.pack(fill="both", expand=True)

        MatrixTable(
            crit_scroll,
            results["criteria_matrix"], criteria,
            title="Original Criteria Matrix"
        ).pack(padx=8, pady=4)

        if results.get("normalized_criteria_matrix") is not None:
            MatrixTable(
                crit_scroll,
                results["normalized_criteria_matrix"], criteria,
                title="Normalized Criteria Matrix"
            ).pack(padx=8, pady=4)


        pv = results["criteria_priority_vector"]
        pv_frame = ctk.CTkFrame(crit_scroll, fg_color="#0d1b2a")
        pv_frame.pack(padx=8, pady=4, fill="x")
        ctk.CTkLabel(pv_frame, text="Priority Vector:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=6, pady=4)
        for crit, w in zip(criteria, pv):
            ctk.CTkLabel(pv_frame, text=f"  {crit}: {w:.6f}").pack(anchor="w", padx=12)


        tabview.add("Alternatives")
        alt_scroll = ctk.CTkScrollableFrame(tabview.tab("Alternatives"), height=300)
        alt_scroll.pack(fill="both", expand=True)

        for crit in criteria:
            if crit in results.get("alt_matrices", {}):
                MatrixTable(
                    alt_scroll,
                    results["alt_matrices"][crit], alternatives,
                    title=f"Criterion: {crit}"
                ).pack(padx=8, pady=4)

                if crit in results.get("normalized_alt_matrices", {}):
                    MatrixTable(
                        alt_scroll,
                        results["normalized_alt_matrices"][crit], alternatives,
                        title=f"Normalized - {crit}"
                    ).pack(padx=8, pady=4)

                if crit in results.get("alt_priority_vectors", {}):
                    pv_a = results["alt_priority_vectors"][crit]
                    pv_f = ctk.CTkFrame(alt_scroll, fg_color="#0d1b2a")
                    pv_f.pack(padx=8, pady=2, fill="x")
                    ctk.CTkLabel(pv_f, text=f"Priority Vector ({crit}):",
                                 font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=6, pady=2)
                    for alt, w in zip(alternatives, pv_a):
                        ctk.CTkLabel(pv_f, text=f"  {alt}: {w:.6f}").pack(anchor="w", padx=12)


        tabview.add("Decision Matrix")
        dm_scroll = ctk.CTkScrollableFrame(tabview.tab("Decision Matrix"), height=300)
        dm_scroll.pack(fill="both", expand=True)


        if results.get("alt_priority_vectors") and results.get("criteria_priority_vector") is not None:
            crit_pv = results["criteria_priority_vector"]
            n_alt = len(alternatives)
            n_crit = len(criteria)
            wdm = np.zeros((n_alt, n_crit))
            for j, crit in enumerate(criteria):
                alt_pv = results["alt_priority_vectors"].get(crit)
                if alt_pv is not None:
                    wdm[:, j] = alt_pv * crit_pv[j]

            MatrixTable(
                dm_scroll, wdm, alternatives, criteria,
                title="Weighted Decision Matrix (alt_priority × criterion_weight)"
            ).pack(padx=8, pady=4)


            scores_f = ctk.CTkFrame(dm_scroll, fg_color="#16213e")
            scores_f.pack(padx=8, pady=4, fill="x")
            ctk.CTkLabel(scores_f, text="Final Weighted Scores:",
                         font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=6, pady=4)
            for alt, score in zip(alternatives, results["weighted_scores"]):
                ctk.CTkLabel(scores_f, text=f"  {alt}: {score:.6f}").pack(anchor="w", padx=12)

    def _build_explanation_section(self, parent):
        ctk.CTkLabel(
            parent, text="🤖  AI Explanation (Mistral)",
            font=ctk.CTkFont(size=16, weight="bold"), text_color="#e9c46a"
        ).pack(anchor="w", pady=(16, 4), padx=10)

        ctrl = ctk.CTkFrame(parent, fg_color="transparent")
        ctrl.pack(anchor="w", padx=10, pady=(0, 6), fill="x")


        ctk.CTkLabel(ctrl, text="Language:",
                     font=ctk.CTkFont(size=12), text_color="gray"
                     ).pack(side="left", padx=(0, 8))


        self._lang_toggle = ctk.CTkSegmentedButton(
            ctrl,
            values=["English", "Francais", "Arabe"],
            command=self._on_lang_toggle,
            font=ctk.CTkFont(size=12),
            width=280
        )
        self._lang_toggle.set("English")
        self._lang_toggle.pack(side="left")


        self._lang_map = {
            "English": "en",
            "Francais": "fr",
            "Arabe":    "ar",
        }


        btn_row = ctk.CTkFrame(parent, fg_color="transparent")
        btn_row.pack(anchor="w", padx=10, pady=(4, 4))
        self.explain_btn = ctk.CTkButton(
            btn_row, text="🤖  Generate Explanation",
            command=self._trigger_explanation,
            fg_color="#4a0e8f", hover_color="#7b2d8b",
            height=36, font=ctk.CTkFont(size=13, weight="bold")
        )
        self.explain_btn.pack(side="left", padx=(0, 10))
        self.explain_status = ctk.CTkLabel(
            btn_row, text="", text_color="#a8dadc", font=ctk.CTkFont(size=12)
        )
        self.explain_status.pack(side="left")

        self.explanation_box = ctk.CTkTextbox(
            parent, height=220,
            font=ctk.CTkFont(size=12),
            fg_color="#0d1b2a", text_color="#e0e0e0",
            wrap="word"
        )
        self.explanation_box.pack(fill="x", padx=10, pady=4)
        self.explanation_box.insert(
            "1.0",
            "Choose a language with the toggle above, then click 'Generate Explanation'."
        )
        self.explanation_box.configure(state="disabled")

    def _on_lang_toggle(self, value: str):

        pass  

    def _trigger_explanation(self):
        label = self._lang_toggle.get()
        lang  = self._lang_map.get(label, "en")
        self.explain_btn.configure(state="disabled", text="⏳  Generating…")
        self.explanation_text = ""
        self.vm.explain_results_async(language=lang)

    def _append_explanation_token(self, token: str):
        self.after(0, self._do_append_token, token)

    def _do_append_token(self, token: str):
        self.explanation_box.configure(state="normal")
        if self.explanation_box.get("1.0", "1.5") == "Click":
            self.explanation_box.delete("1.0", "end")
        self.explanation_box.insert("end", token)
        self.explanation_box.see("end")
        self.explanation_box.configure(state="disabled")
        self.explanation_text += token

    def _on_explanation_done(self):
        self.after(0, lambda: self.explain_status.configure(text="✓ Explanation complete"))
        self.after(0, lambda: self.explain_btn.configure(
            state="normal", text="🤖  Generate Explanation"))

    def _build_action_buttons(self):
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(
            btn_frame, text=" Export CSV",
            command=self._export_csv,
            fg_color="#2d6a4f", hover_color="#1b4332", width=140
        ).pack(side="left", padx=6)

        ctk.CTkButton(
            btn_frame, text=" Save PDF",
            command=self._export_pdf,
            fg_color="#1d3557", hover_color="#457b9d", width=140
        ).pack(side="left", padx=6)

        ctk.CTkButton(
            btn_frame, text=" Start New",
            command=self.on_restart,
            fg_color="#6b2737", hover_color="#9b2335", width=140
        ).pack(side="left", padx=6)

    def _export_csv(self):
        from tkinter import filedialog
        import os
        output_dir = filedialog.askdirectory(title="Select output folder for CSV files")
        if output_dir:
            path = self.vm.export_csv(output_dir)
            self._show_toast(f"CSV saved to:\n{path}")

    def _export_pdf(self):
        from tkinter import filedialog
        filepath = filedialog.asksaveasfilename(
            title="Save PDF Report",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        if filepath:
            success = self.vm.export_pdf(filepath, self.explanation_text)
            if success:
                self._show_toast(f"PDF saved: {filepath}")
            else:
                self._show_toast("PDF export failed.\nInstall 'reportlab' for PDF support.")

    def _show_toast(self, msg: str):
        toast = ctk.CTkToplevel(self)
        toast.title("")
        toast.geometry("400x80")
        ctk.CTkLabel(toast, text=msg, wraplength=380).pack(expand=True, padx=10, pady=10)
        toast.after(3000, toast.destroy)
