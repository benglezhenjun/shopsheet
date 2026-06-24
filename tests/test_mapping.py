import pandas as pd
import pytest

from shopsheet.mapping import normalize_orders, normalize_refunds, normalize_skus


def test_normalize_orders_maps_common_chinese_headers():
    raw = pd.DataFrame(
        [
            {
                "订单编号": "O-1001",
                "商品编码": "SKU-RED-M",
                "购买数量": "2",
                "成交单价": "79.90",
                "收货手机号": "13800138000",
                "收货地址": "Shanghai Pudong",
                "下单时间": "2026-06-01",
            }
        ]
    )

    normalized = normalize_orders(raw)

    assert normalized.to_dict("records") == [
        {
            "order_id": "O-1001",
            "sku": "SKU-RED-M",
            "quantity": 2,
            "unit_price": 79.90,
            "phone": "13800138000",
            "shipping_address": "Shanghai Pudong",
            "order_date": "2026-06-01",
        }
    ]


def test_normalize_orders_cleans_float_like_phone_values():
    raw = pd.DataFrame(
        [
            {
                "order_id": "O-1001",
                "sku": "SKU-RED-M",
                "quantity": 1,
                "unit_price": 79.90,
                "phone": 13800138000,
                "shipping_address": "Shanghai Pudong",
            },
            {
                "order_id": "O-1002",
                "sku": "SKU-BLUE-S",
                "quantity": 1,
                "unit_price": 129.00,
                "phone": None,
                "shipping_address": "Hangzhou Xihu",
            },
            {
                "order_id": "O-1003",
                "sku": "SKU-GREEN-L",
                "quantity": 1,
                "unit_price": 49.90,
                "phone": 13900139000,
                "shipping_address": "Shenzhen Nanshan",
            },
        ]
    )

    normalized = normalize_orders(raw)

    assert normalized["phone"].tolist() == ["13800138000", "", "13900139000"]


def test_normalize_skus_maps_common_headers():
    raw = pd.DataFrame(
        [{"商品编码": "SKU-RED-M", "商品名称": "Red T-Shirt M", "成本价": "35.00"}]
    )

    normalized = normalize_skus(raw)

    assert normalized.to_dict("records") == [
        {"sku": "SKU-RED-M", "product_name": "Red T-Shirt M", "cost": 35.00}
    ]


def test_normalize_refunds_maps_common_headers():
    raw = pd.DataFrame(
        [{"退款编号": "R-9001", "订单编号": "O-1001", "退款金额": "20.00", "退款原因": "partial"}]
    )

    normalized = normalize_refunds(raw)

    assert normalized.to_dict("records") == [
        {
            "refund_id": "R-9001",
            "order_id": "O-1001",
            "refund_amount": 20.00,
            "reason": "partial",
        }
    ]


def test_normalize_orders_rejects_missing_required_columns():
    raw = pd.DataFrame([{"订单编号": "O-1001"}])

    with pytest.raises(ValueError, match="Missing required order columns"):
        normalize_orders(raw)
