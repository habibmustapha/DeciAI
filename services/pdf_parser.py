import re
from typing import Optional, Tuple, List
import numpy as np


def _clean_number(text: str) -> float:

    text = str(text).strip()
    text = text.replace(" ", "")
    comma_count = text.count(",")
    if comma_count == 1:
        parts = text.split(",")
        if len(parts[1]) <= 3:
            text = text.replace(",", ".")
        else:
            text = text.replace(",", "")
    try:
        return float(text)
    except ValueError:
        return 0.0


def extract_from_pdf(
    pdf_path: str,
    page: str = "1"
) -> Optional[Tuple[List[str], List[str], np.ndarray]]:

    try:
        import camelot
    except ImportError:
        raise ImportError(
            "camelot-py is not installed.\n"
            "Install it with:  pip install camelot-py[cv]"
        )

    try:
        tables = camelot.read_pdf(pdf_path, pages=page, flavor="lattice")
        if len(tables) == 0:
            tables = camelot.read_pdf(pdf_path, pages=page, flavor="stream")
        if len(tables) == 0:
            return None

        import pandas as pd
        df = tables[0].df

        df.columns = df.iloc[0]
        df = df[1:].reset_index(drop=True)

        df = df.replace("", np.nan).dropna(how="all").dropna(axis=1, how="all")
        df = df.fillna("0")

        alternatives = [str(v).strip() for v in df.iloc[:, 0].tolist()]
        criteria     = [str(c).strip() for c in df.columns[1:].tolist()]

        n_alt  = len(alternatives)
        n_crit = len(criteria)
        matrix = np.zeros((n_alt, n_crit))

        for i in range(n_alt):
            for j in range(n_crit):
                raw = df.iloc[i, j + 1]
                matrix[i][j] = _clean_number(raw)

        return alternatives, criteria, matrix

    except Exception as e:
        raise RuntimeError(f"PDF parsing failed: {e}")
