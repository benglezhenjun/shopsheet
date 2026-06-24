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
    assert bundle.metrics["issue_count"] == 7
    assert bundle.clean_orders[0]["line_amount"] == 159.80
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
    assert bundle.metrics["issue_count"] == 2
    assert bundle.clean_orders[0]["order_id"] == "CN-1001"
    assert bundle.issue_rows[0]["source_table"] == "orders"
