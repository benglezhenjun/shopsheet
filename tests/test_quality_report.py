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
    assert report.metrics["estimated_gross_margin"] == 212.50

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
    ]


def test_analyze_shop_data_flags_invalid_numeric_cells_before_zero_fill():
    orders = pd.DataFrame(
        [
            {
                "order_id": "O-3001",
                "sku": "SKU-RED-M",
                "quantity": "x",
                "unit_price": "79.90",
                "phone": "13800138000",
                "shipping_address": "Shanghai Pudong",
            },
            {
                "order_id": "O-3002",
                "sku": "SKU-RED-M",
                "quantity": "1",
                "unit_price": "abc",
                "phone": "13900139000",
                "shipping_address": "Hangzhou Xihu",
            },
        ]
    )
    skus = pd.DataFrame(
        [{"sku": "SKU-RED-M", "product_name": "Red T-Shirt M", "cost": "bad"}]
    )
    refunds = pd.DataFrame(
        [{"refund_id": "R-3001", "order_id": "O-3001", "refund_amount": "bad"}]
    )

    report = analyze_shop_data(orders, skus, refunds)

    issue_codes = [issue.code for issue in report.issues]
    assert "invalid_quantity" in issue_codes
    assert "invalid_unit_price" in issue_codes
    assert "invalid_cost" in issue_codes
    assert "invalid_refund_amount" in issue_codes


def test_analyze_shop_data_does_not_flag_valid_integer_phones_after_blank_values():
    orders = pd.DataFrame(
        [
            {
                "order_id": "O-4001",
                "sku": "SKU-RED-M",
                "quantity": 1,
                "unit_price": 79.90,
                "phone": "13800138000",
                "shipping_address": "Shanghai Pudong",
            },
            {
                "order_id": "O-4002",
                "sku": "SKU-RED-M",
                "quantity": 1,
                "unit_price": 79.90,
                "phone": "",
                "shipping_address": "Hangzhou Xihu",
            },
            {
                "order_id": "O-4003",
                "sku": "SKU-RED-M",
                "quantity": 1,
                "unit_price": 79.90,
                "phone": "13900139000",
                "shipping_address": "Shenzhen Nanshan",
            },
        ]
    )
    skus = pd.DataFrame(
        [{"sku": "SKU-RED-M", "product_name": "Red T-Shirt M", "cost": 35.00}]
    )
    refunds = pd.DataFrame(columns=["refund_id", "order_id", "refund_amount"])

    report = analyze_shop_data(orders, skus, refunds)

    invalid_phone = next(issue for issue in report.issues if issue.code == "invalid_phone")
    assert invalid_phone.rows == [3]


def test_refund_exceeds_only_applies_to_known_orders_above_positive_amount():
    orders = pd.DataFrame(
        [
            {
                "order_id": "O-5001",
                "sku": "SKU-RED-M",
                "quantity": 1,
                "unit_price": 100.00,
                "phone": "13800138000",
                "shipping_address": "Shanghai Pudong",
            }
        ]
    )
    skus = pd.DataFrame(
        [{"sku": "SKU-RED-M", "product_name": "Red T-Shirt M", "cost": 35.00}]
    )
    refunds = pd.DataFrame(
        [
            {"refund_id": "R-5001", "order_id": "O-404", "refund_amount": 10.00},
            {"refund_id": "R-5002", "order_id": "O-5001", "refund_amount": 99.00},
        ]
    )

    report = analyze_shop_data(orders, skus, refunds)

    issue_codes = [issue.code for issue in report.issues]
    assert "refund_unknown_order" in issue_codes
    assert "refund_exceeds_order_amount" not in issue_codes
