from __future__ import annotations

from pathlib import Path

import pandas as pd

IDENTIFIER_COLUMNS = {
    "order_id",
    "order no",
    "order number",
    "订单编号",
    "订单号",
    "sku",
    "商品编码",
    "商家编码",
    "商品sku",
    "规格编码",
    "refund_id",
    "refund no",
    "退款编号",
    "退款单号",
}


def load_table(path: str | Path) -> pd.DataFrame:
    table_path = Path(path)
    suffix = table_path.suffix.lower()

    if suffix == ".csv":
        return _read_csv(table_path)
    if suffix in {".xlsx", ".xlsm"}:
        return pd.read_excel(table_path, dtype=_identifier_dtypes())

    raise ValueError(
        f"Unsupported table format '{suffix}'. Use CSV or XLSX merchant exports."
    )


def _read_csv(path: Path) -> pd.DataFrame:
    for encoding in ("utf-8-sig", "gb18030"):
        try:
            return pd.read_csv(path, encoding=encoding, dtype=_identifier_dtypes())
        except UnicodeDecodeError:
            continue
    return pd.read_csv(path, encoding="gb18030", dtype=_identifier_dtypes())


def _identifier_dtypes() -> dict[str, str]:
    return {column: "string" for column in IDENTIFIER_COLUMNS}
