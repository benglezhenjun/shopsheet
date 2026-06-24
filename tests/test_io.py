from pathlib import Path

import pandas as pd
import pytest

from shopsheet.io import load_table


def test_load_table_reads_csv(tmp_path: Path):
    csv_path = tmp_path / "orders.csv"
    csv_path.write_text("order_id,amount\nO-1001,19.90\n", encoding="utf-8")

    table = load_table(csv_path)

    assert table.to_dict("records") == [{"order_id": "O-1001", "amount": 19.90}]


def test_load_table_reads_gb18030_csv_and_preserves_identifier_strings(tmp_path: Path):
    csv_path = tmp_path / "orders.csv"
    csv_path.write_bytes(
        (
            "订单编号,商品编码,购买数量,成交单价,收货手机号,收货地址\n"
            "O-1001,00123,2,19.90,13800138000,Shanghai Pudong\n"
        ).encode("gb18030")
    )

    table = load_table(csv_path)

    assert table.loc[0, "商品编码"] == "00123"


def test_load_table_reads_xlsx(tmp_path: Path):
    xlsx_path = tmp_path / "orders.xlsx"
    pd.DataFrame([{"order_id": "O-1001", "amount": 19.90}]).to_excel(
        xlsx_path, index=False
    )

    table = load_table(xlsx_path)

    assert table.to_dict("records") == [{"order_id": "O-1001", "amount": 19.90}]


def test_load_table_reads_xlsx_and_preserves_identifier_strings(tmp_path: Path):
    xlsx_path = tmp_path / "skus.xlsx"
    pd.DataFrame([{"sku": "00123", "product_name": "Widget", "cost": "3.50"}]).to_excel(
        xlsx_path, index=False
    )

    table = load_table(xlsx_path)

    assert table.loc[0, "sku"] == "00123"


def test_load_table_rejects_unsupported_suffix(tmp_path: Path):
    txt_path = tmp_path / "orders.txt"
    txt_path.write_text("not a table", encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported table format"):
        load_table(txt_path)
