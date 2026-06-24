import pandas as pd

from shopsheet.quality import analyze_shop_data


def test_analyze_shop_data_flags_core_merchant_data_issues():
    orders = pd.DataFrame(
        [
            {
                "order_id": "O-1001",
                "sku": "SKU-RED-M",
                "quantity": 2,
                "unit_price": 79.90,
                "phone": "13800138000",
                "shipping_address": "Shanghai Pudong",
            },
            {
                "order_id": "O-1002",
                "sku": "SKU-BLUE-S",
                "quantity": 1,
                "unit_price": 129.00,
                "phone": "not-a-phone",
                "shipping_address": "Hangzhou Xihu",
            },
            {
                "order_id": "O-1002",
                "sku": "SKU-BLUE-S",
                "quantity": 1,
                "unit_price": 129.00,
                "phone": "13900139000",
                "shipping_address": "Hangzhou Xihu",
            },
            {
                "order_id": "O-1003",
                "sku": "SKU-MISSING",
                "quantity": 1,
                "unit_price": 59.00,
                "phone": "13700137000",
                "shipping_address": "Beijing Chaoyang",
            },
            {
                "order_id": "O-1004",
                "sku": "SKU-RED-M",
                "quantity": -1,
                "unit_price": 79.90,
                "phone": "13600136000",
                "shipping_address": "Shenzhen Nanshan",
            },
            {
                "order_id": "O-1005",
                "sku": "SKU-GREEN-L",
                "quantity": 3,
                "unit_price": 49.90,
                "phone": "13500135000",
                "shipping_address": "",
            },
        ]
    )
    skus = pd.DataFrame(
        [
            {"sku": "SKU-RED-M", "product_name": "Red T-Shirt M", "cost": 35.00},
            {"sku": "SKU-BLUE-S", "product_name": "Blue Hoodie S", "cost": 70.00},
            {"sku": "SKU-GREEN-L", "product_name": "Green Socks L", "cost": 15.00},
        ]
    )
    refunds = pd.DataFrame(
        [
            {"refund_id": "R-9001", "order_id": "O-1001", "refund_amount": 20.00},
            {"refund_id": "R-9002", "order_id": "O-1003", "refund_amount": 80.00},
        ]
    )

    report = analyze_shop_data(orders, skus, refunds)

    assert report.metrics["order_rows"] == 6
    assert report.metrics["sku_rows"] == 3
    assert report.metrics["refund_rows"] == 2
    assert report.metrics["gross_sales"] == 626.50
    assert report.metrics["refund_amount"] == 100.00
    assert report.metrics["estimated_gross_margin"] == 271.50

    issue_codes = [issue.code for issue in report.issues]
    assert issue_codes == [
        "duplicate_order_id",
        "invalid_phone",
        "missing_sku",
        "negative_quantity",
        "missing_shipping_address",
        "refund_exceeds_order_amount",
    ]


def test_analyze_shop_data_flags_sku_refund_and_date_quality_issues():
    orders = pd.DataFrame(
        [
            {
                "order_id": "O-2001",
                "sku": "SKU-RED-M",
                "quantity": 1,
                "unit_price": 79.90,
                "phone": "13800138000",
                "shipping_address": "Shanghai Pudong",
                "order_date": "not-a-date",
            }
        ]
    )
    skus = pd.DataFrame(
        [
            {"sku": "SKU-RED-M", "product_name": "Red T-Shirt M", "cost": 35.00},
            {"sku": "SKU-RED-M", "product_name": "Red T-Shirt Duplicate", "cost": 36.00},
            {"sku": "SKU-BAD-COST", "product_name": "Bad Cost", "cost": -1.00},
        ]
    )
    refunds = pd.DataFrame(
        [{"refund_id": "R-9999", "order_id": "O-404", "refund_amount": 10.00}]
    )

    report = analyze_shop_data(orders, skus, refunds)

    issue_codes = [issue.code for issue in report.issues]
    assert issue_codes == [
        "invalid_order_date",
        "duplicate_sku",
        "negative_sku_cost",
        "refund_unknown_order",
        "refund_exceeds_order_amount",
    ]
