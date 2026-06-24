from pathlib import Path

import pandas as pd
import pytest

from shopsheet.io import load_table


def test_load_table_reads_csv(tmp_path: Path):
    csv_path = tmp_path / "orders.csv"
    csv_path.write_text("order_id,amount\nO-1001,19.90\n", encoding="utf-8")

    table = load_table(csv_path)

    assert table.to_dict("records") == [{"order_id": "O-1001", "amount": 19.90}]


def test_load_table_reads_xlsx(tmp_path: Path):
    xlsx_path = tmp_path / "orders.xlsx"
    pd.DataFrame([{"order_id": "O-1001", "amount": 19.90}]).to_excel(
        xlsx_path, index=False
    )

    table = load_table(xlsx_path)

    assert table.to_dict("records") == [{"order_id": "O-1001", "amount": 19.90}]


def test_load_table_rejects_unsupported_suffix(tmp_path: Path):
    txt_path = tmp_path / "orders.txt"
    txt_path.write_text("not a table", encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported table format"):
        load_table(txt_path)
