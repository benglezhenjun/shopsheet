from pathlib import Path

from shopsheet.pipeline import build_audit_bundle


def test_build_audit_bundle_from_example_files():
    root = Path(__file__).resolve().parents[1]

    bundle = build_audit_bundle(
        order_path=root / "examples" / "orders_messy.csv",
        sku_path=root / "examples" / "skus.csv",
        refund_path=root / "examples" / "refunds.csv",
    )

    assert bundle.metrics["order_rows"] == 6
    assert bundle.metrics["clean_order_count"] == 1
    assert bundle.metrics["excluded_order_count"] == 5
    assert bundle.metrics["issue_count"] == 7
    assert [order["order_id"] for order in bundle.clean_orders] == ["O-1001"]
    assert bundle.clean_orders[0]["line_amount"] == 159.80
    assert bundle.clean_orders[0]["estimated_line_margin"] == 89.80
    assert "unit_cost" not in bundle.clean_orders[0]
    assert bundle.issue_rows[0]["code"] == "duplicate_order_id"
    assert bundle.issue_rows[0]["source_table"] == "orders"
    assert bundle.issue_rows[0]["row"] == 3
    assert "# ShopSheet Quality Report" in bundle.markdown_report


def test_build_audit_bundle_from_chinese_header_examples():
    root = Path(__file__).resolve().parents[1]

    bundle = build_audit_bundle(
        order_path=root / "examples" / "orders_chinese_headers.csv",
        sku_path=root / "examples" / "skus_chinese_headers.csv",
        refund_path=root / "examples" / "refunds_chinese_headers.csv",
    )

    assert bundle.metrics["order_rows"] == 3
    assert bundle.metrics["clean_order_count"] == 1
    assert bundle.metrics["excluded_order_count"] == 2
    assert bundle.metrics["issue_count"] == 2
    assert bundle.clean_orders[0]["order_id"] == "CN-1001"
    assert bundle.issue_rows[0]["source_table"] == "orders"


def test_build_audit_bundle_handles_header_only_inputs(tmp_path: Path):
    orders = tmp_path / "orders.csv"
    skus = tmp_path / "skus.csv"
    refunds = tmp_path / "refunds.csv"
    orders.write_text(
        "order_id,sku,quantity,unit_price,phone,shipping_address,order_date\n",
        encoding="utf-8",
    )
    skus.write_text("sku,product_name,cost\n", encoding="utf-8")
    refunds.write_text("refund_id,order_id,refund_amount,reason\n", encoding="utf-8")

    bundle = build_audit_bundle(order_path=orders, sku_path=skus, refund_path=refunds)

    assert bundle.metrics["order_rows"] == 0
    assert bundle.metrics["sku_rows"] == 0
    assert bundle.metrics["refund_rows"] == 0
    assert bundle.metrics["clean_order_count"] == 0
    assert bundle.metrics["excluded_order_count"] == 0
    assert bundle.metrics["issue_count"] == 0
    assert bundle.clean_orders == []
