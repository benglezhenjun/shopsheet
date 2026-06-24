from pathlib import Path

from shopsheet.exports import build_export_package
from shopsheet.pipeline import build_audit_bundle


def test_build_export_package_contains_merchant_deliverables():
    root = Path(__file__).resolve().parents[1]
    bundle = build_audit_bundle(
        order_path=root / "examples" / "orders_messy.csv",
        sku_path=root / "examples" / "skus.csv",
        refund_path=root / "examples" / "refunds.csv",
    )

    package = build_export_package(bundle)

    assert set(package.files) == {
        "clean_orders.csv",
        "issue_rows.csv",
        "quality_report.md",
    }
    assert "order_id,sku,quantity,unit_price" in package.files["clean_orders.csv"]
    assert "O-1001,SKU-RED-M,2,79.9" in package.files["clean_orders.csv"]
    assert "code,message,source_table,row" in package.files["issue_rows.csv"]
    assert "duplicate_order_id,Order ID appears more than once.,orders,3" in package.files[
        "issue_rows.csv"
    ]
    assert package.files["quality_report.md"].startswith("# ShopSheet Quality Report")
