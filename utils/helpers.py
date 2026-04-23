import csv
import os
import numpy as np
from typing import List, Optional
from datetime import datetime


def export_matrix_to_csv(
    matrix: np.ndarray,
    labels: List[str],
    filepath: str,
    title: str = ""
):

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if title:
            writer.writerow([title])
            writer.writerow([])
        writer.writerow([""] + labels)

        for i, label in enumerate(labels):
            row = [label] + [f"{matrix[i][j]:.6f}" for j in range(len(labels))]
            writer.writerow(row)


def export_all_results_to_csv(results: dict, output_dir: str):

    os.makedirs(output_dir, exist_ok=True)
    criteria = results["criteria"]
    alternatives = results["alternatives"]


    export_matrix_to_csv(
        results["criteria_matrix"],
        criteria,
        os.path.join(output_dir, "criteria_matrix.csv"),
        "Criteria Pairwise Comparison Matrix"
    )


    if results["normalized_criteria_matrix"] is not None:
        export_matrix_to_csv(
            results["normalized_criteria_matrix"],
            criteria,
            os.path.join(output_dir, "criteria_normalized.csv"),
            "Normalized Criteria Matrix"
        )


    for crit in criteria:
        if crit in results["alt_matrices"]:
            safe_name = crit.replace(" ", "_").replace("/", "-")
            export_matrix_to_csv(
                results["alt_matrices"][crit],
                alternatives,
                os.path.join(output_dir, f"alt_matrix_{safe_name}.csv"),
                f"Alternative Matrix - {crit}"
            )


    if results["ranking"]:
        with open(os.path.join(output_dir, "ranking.csv"), "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Rank", "Alternative", "Score"])
            for rank, name, score in results["ranking"]:
                writer.writerow([rank, name, f"{score:.6f}"])

    return output_dir


def format_number(value: float, decimals: int = 4) -> str:
    return f"{value:.{decimals}f}"


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def generate_pdf_report(results: dict, goal: str, explanation: str, filepath: str):

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        )
        from reportlab.lib import colors

        doc = SimpleDocTemplate(filepath, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []


        title_style = ParagraphStyle("Title", parent=styles["Title"], fontSize=16)
        story.append(Paragraph("AHP Decision Analysis Report", title_style))
        story.append(Spacer(1, 0.5 * cm))
        story.append(Paragraph(f"<b>Goal:</b> {goal}", styles["Normal"]))
        story.append(Spacer(1, 0.3 * cm))


        story.append(Paragraph("<b>Final Ranking</b>", styles["Heading2"]))
        table_data = [["Rank", "Alternative", "Score"]]
        for rank, name, score in results["ranking"]:
            table_data.append([str(rank), name, f"{score:.4f}"])

        t = Table(table_data, colWidths=[2*cm, 8*cm, 4*cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2b5797")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.5 * cm))

        if explanation:
            story.append(Paragraph("<b>AI Explanation</b>", styles["Heading2"]))
            for para in explanation.split("\n\n"):
                if para.strip():
                    story.append(Paragraph(para.strip(), styles["Normal"]))
                    story.append(Spacer(1, 0.2 * cm))

        doc.build(story)
        return True

    except ImportError:
        return False
    except Exception:
        return False
