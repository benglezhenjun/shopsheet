from __future__ import annotations

import pandas as pd


def enrich_orders(orders: pd.DataFrame, skus: pd.DataFrame) -> pd.DataFrame:
    output = orders.copy()
    quantity = pd.to_numeric(output["quantity"], errors="coerce").fillna(0)
    unit_price = pd.to_numeric(output["unit_price"], errors="coerce").fillna(0)
    unit_cost = output["sku"].astype(str).map(_sku_cost_lookup(skus))

    output["line_amount"] = (quantity * unit_price).round(2)
    output["unit_cost"] = unit_cost
    output["estimated_line_margin"] = (
        output["line_amount"] - quantity * unit_cost.fillna(0)
    ).round(2)
    return output


def _sku_cost_lookup(skus: pd.DataFrame) -> dict[str, float]:
    costs = pd.to_numeric(skus["cost"], errors="coerce")
    return {
        str(sku): float(cost)
        for sku, cost in zip(skus["sku"], costs, strict=True)
        if not pd.isna(cost)
    }
