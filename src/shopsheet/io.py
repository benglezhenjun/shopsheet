from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_table(path: str | Path) -> pd.DataFrame:
    table_path = Path(path)
    suffix = table_path.suffix.lower()

    if suffix == ".csv":
        return pd.read_csv(table_path)
    if suffix in {".xlsx", ".xlsm"}:
        return pd.read_excel(table_path)

    raise ValueError(
        f"Unsupported table format '{suffix}'. Use CSV or XLSX merchant exports."
    )
