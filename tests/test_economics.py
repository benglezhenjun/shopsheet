import pandas as pd

from shopsheet.economics import enrich_orders


def test_enrich_orders_adds_line_amount_and_margin_columns():
    orders = pd.DataFrame(
        [
            {"order_id": "O-1001", "sku": "SKU-RED-M", "quantity": "2", "unit_price": "10.00"},
            {"order_id": "O-1002", "sku": "SKU-MISSING", "quantity": "1", "unit_price": "5.00"},
        ]
    )
    skus = pd.DataFrame([{"sku": "SKU-RED-M", "product_name": "Red", "cost": "3.00"}])

    enriched = enrich_orders(orders, skus)

    assert enriched["line_amount"].tolist() == [20.00, 5.00]
    assert enriched.loc[0, "unit_cost"] == 3.00
    assert pd.isna(enriched.loc[1, "unit_cost"])
    assert enriched["estimated_line_margin"].tolist() == [14.00, 5.00]
