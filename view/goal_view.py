import customtkinter as ctk
from typing import Callable, List


class GoalView(ctk.CTkFrame):
    def __init__(self, parent, on_next: Callable, **kwargs):
        super().__init__(parent, **kwargs)
        self.on_next = on_next
        self.criteria_entries: List[ctk.CTkEntry] = []
        self.alt_entries: List[ctk.CTkEntry] = []
        self.pdf_matrix = None
        self._build_ui()

    def _build_ui(self):
        ctk.CTkLabel(
            self, text="AHP Decision Setup",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=(20, 4))
        ctk.CTkLabel(
            self,
            text="Fill in the goal and names manually — or upload a PDF table to import everything automatically.",
            font=ctk.CTkFont(size=12), text_color="gray", wraplength=700
        ).pack(pady=(0, 10))

        body = ctk.CTkScrollableFrame(self)
        body.pack(fill="both", expand=True, padx=30, pady=0)

        pdf_banner = ctk.CTkFrame(body, fg_color="#16213e", corner_radius=10)
        pdf_banner.pack(fill="x", pady=(4, 18))

        ctk.CTkLabel(
            pdf_banner,
            text="Import from PDF",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="#e9c46a"
        ).pack(anchor="w", padx=14, pady=(10, 2))
        ctk.CTkLabel(
            pdf_banner,
            text="Upload a PDF that contains a table with suppliers as rows and criteria as columns. "
                 "The app will extract all names and values automatically.",
            font=ctk.CTkFont(size=11), text_color="gray", wraplength=800
        ).pack(anchor="w", padx=14, pady=(0, 8))

        btn_row = ctk.CTkFrame(pdf_banner, fg_color="transparent")
        btn_row.pack(anchor="w", padx=14, pady=(0, 12))

        ctk.CTkButton(
            btn_row,
            text="Choose PDF File",
            width=180, height=36,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#1d3557", hover_color="#457b9d",
            command=self._import_pdf
        ).pack(side="left", padx=(0, 12))

        self._pdf_status = ctk.CTkLabel(
            btn_row, text="No file selected",
            font=ctk.CTkFont(size=12), text_color="gray"
        )
        self._pdf_status.pack(side="left")


        ctk.CTkLabel(body, text="Decision Goal:",
                     font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(4, 3))
        self.goal_entry = ctk.CTkEntry(
            body, placeholder_text="e.g. Select the best milk supplier",
            height=40, font=ctk.CTkFont(size=14)
        )
        self.goal_entry.pack(fill="x", pady=(0, 16))


        ctk.CTkLabel(
            body, text="Criteria  (table columns)",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(
            body,
            text="These become the columns of the data table. Auto-filled when importing from PDF.",
            font=ctk.CTkFont(size=11), text_color="gray"
        ).pack(anchor="w", pady=(0, 6))

        self.crit_container = ctk.CTkFrame(body, fg_color="transparent")
        self.crit_container.pack(fill="x")
        for p in ["e.g. Volume de lait (VL)", "e.g. Taux de matière grasse (MG)",
                  "e.g. Taux de matière protéique (MP)", "e.g. Densité (D)"]:
            self._add_row(self.crit_container, self.criteria_entries, p)

        ctk.CTkButton(
            body, text="+ Add Criterion", width=160,
            fg_color="#2d6a4f", hover_color="#1b4332",
            command=lambda: self._add_row(self.crit_container, self.criteria_entries, "Criterion")
        ).pack(anchor="w", pady=6)

        ctk.CTkButton(
            body,
            text="Generate Criteria (AI)",
            width=200,
            fg_color="#6c5ce7",
            hover_color="#5a4bd1",
            command=self._generate_criteria_ai
        ).pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(
            body, text="Alternatives  (table rows)",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", pady=(16, 4))
        ctk.CTkLabel(
            body,
            text="These become the rows of the data table. Auto-filled when importing from PDF.",
            font=ctk.CTkFont(size=11), text_color="gray"
        ).pack(anchor="w", pady=(0, 6))

        self.alt_container = ctk.CTkFrame(body, fg_color="transparent")
        self.alt_container.pack(fill="x")
        for p in [f"e.g. F{i}" for i in range(1, 4)]:
            self._add_row(self.alt_container, self.alt_entries, p)

        ctk.CTkButton(
            body, text="+ Add Alternative", width=160,
            fg_color="#2d6a4f", hover_color="#1b4332",
            command=lambda: self._add_row(self.alt_container, self.alt_entries, "Alternative")
        ).pack(anchor="w", pady=6)


        self.error_lbl = ctk.CTkLabel(
            body, text="", text_color="#e63946", font=ctk.CTkFont(size=12)
        )
        self.error_lbl.pack(pady=(10, 0))

        ctk.CTkButton(
            body, text="Next: Enter Data Table  →",
            command=self._handle_next,
            height=44, font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#1d3557", hover_color="#457b9d"
        ).pack(pady=14)



    def _import_pdf(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(
            title="Select PDF file",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if not path:
            return

        self._pdf_status.configure(text="Parsing…", text_color="#a8dadc")
        self.update()  

        try:
            from services.pdf_parser import extract_from_pdf
            result = extract_from_pdf(path)
            if result is None:
                self._pdf_status.configure(
                    text="No table found in PDF.", text_color="#e63946")
                return

            alternatives, criteria, matrix = result
            self.pdf_matrix = matrix  


            for w in self.crit_container.winfo_children():
                w.destroy()
            self.criteria_entries.clear()
            for c in criteria:
                self._add_row(self.crit_container, self.criteria_entries, "", prefill=c)


            for w in self.alt_container.winfo_children():
                w.destroy()
            self.alt_entries.clear()
            for a in alternatives:
                self._add_row(self.alt_container, self.alt_entries, "", prefill=a)

            fname = path.split("/")[-1].split("\\")[-1]
            self._pdf_status.configure(
                text=f"✓  {fname}  —  {len(alternatives)} alternatives · {len(criteria)} criteria",
                text_color="#2d6a4f"
            )
            self.error_lbl.configure(text="")

        except ImportError as e:
            self._pdf_status.configure(
                text="camelot-py not installed. Run: pip install camelot-py[cv]",
                text_color="#e63946")
        except Exception as e:
            self._pdf_status.configure(
                text=f"Error: {str(e)[:80]}",
                text_color="#e63946")



    def _add_row(self, container, entry_list, placeholder, prefill=""):
        row = ctk.CTkFrame(container, fg_color="transparent")
        row.pack(fill="x", pady=2)
        entry = ctk.CTkEntry(row, placeholder_text=placeholder, height=34)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        if prefill:
            entry.insert(0, prefill)

        def remove(r=row, e=entry):
            if e in entry_list:
                entry_list.remove(e)
            r.destroy()

        ctk.CTkButton(
            row, text="✕", width=34, height=34,
            fg_color="#6b2737", hover_color="#9b2335",
            command=remove
        ).pack(side="right")
        entry_list.append(entry)


    def _generate_criteria_ai(self):
        goal = self.goal_entry.get().strip()

        if not goal:
            self.error_lbl.configure(text="⚠ Enter a goal first to generate criteria.")
            return

        self.error_lbl.configure(text="Generating criteria with AI...")

        try:
            from services.ai_generator import generate_criteria

            criteria = generate_criteria(goal)

            if not criteria:
                self.error_lbl.configure(text="⚠ AI returned no results.")
                return

            # Clear existing criteria
            for w in self.crit_container.winfo_children():
                w.destroy()
            self.criteria_entries.clear()

            # Add AI-generated criteria
            for c in criteria:
                self._add_row(self.crit_container, self.criteria_entries, "", prefill=c)

            self.error_lbl.configure(text="Criteria generated successfully!")

        except Exception as e:
            self.error_lbl.configure(text=f"Error: {str(e)[:80]}")

    def _handle_next(self):
        goal         = self.goal_entry.get().strip()
        criteria     = [e.get().strip() for e in self.criteria_entries if e.get().strip()]
        alternatives = [e.get().strip() for e in self.alt_entries    if e.get().strip()]

        if not goal:
            self.error_lbl.configure(text="⚠ Please enter a decision goal.")
            return
        if len(criteria) < 2:
            self.error_lbl.configure(text="⚠ Add at least 2 criteria.")
            return
        if len(alternatives) < 2:
            self.error_lbl.configure(text="⚠ Add at least 2 alternatives.")
            return

        self.error_lbl.configure(text="")
        self.on_next(goal, criteria, alternatives, self.pdf_matrix)
