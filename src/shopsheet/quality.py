from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class QualityIssue:
    code: str
    message: str
    rows: list[int]


@dataclass(frozen=True)
class QualityReport:
    metrics: dict[str, float | int]
    issues: list[QualityIssue]


def analyze_shop_data(
    orders: pd.DataFrame, skus: pd.DataFrame, refunds: pd.DataFrame
) -> QualityReport:
    normalized_orders = orders.copy()
    normalized_skus = skus.copy()
    normalized_refunds = refunds.copy()

    normalized_orders["quantity"] = pd.to_numeric(
        normalized_orders["quantity"], errors="coerce"
    ).fillna(0)
    normalized_orders["unit_price"] = pd.to_numeric(
        normalized_orders["unit_price"], errors="coerce"
    ).fillna(0)
    normalized_skus["cost"] = pd.to_numeric(normalized_skus["cost"], errors="coerce").fillna(0)
    normalized_refunds["refund_amount"] = pd.to_numeric(
        normalized_refunds["refund_amount"], errors="coerce"
    ).fillna(0)

    positive_orders = normalized_orders[normalized_orders["quantity"] > 0].copy()
    positive_orders["line_amount"] = positive_orders["quantity"] * positive_orders["unit_price"]

    sku_costs = normalized_skus.set_index("sku")["cost"].to_dict()
    positive_orders["line_cost"] = positive_orders.apply(
        lambda row: row["quantity"] * sku_costs.get(row["sku"], 0),
        axis=1,
    )

    gross_sales = round(float(positive_orders["line_amount"].sum()), 2)
    refund_amount = round(float(normalized_refunds["refund_amount"].sum()), 2)
    gross_margin = round(gross_sales - float(positive_orders["line_cost"].sum()) - refund_amount, 2)

    metrics: dict[str, float | int] = {
        "order_rows": int(len(normalized_orders)),
        "sku_rows": int(len(normalized_skus)),
        "refund_rows": int(len(normalized_refunds)),
        "gross_sales": gross_sales,
        "refund_amount": refund_amount,
        "estimated_gross_margin": gross_margin,
    }

    issues: list[QualityIssue] = []

    duplicated = normalized_orders[normalized_orders["order_id"].duplicated(keep=False)]
    if not duplicated.empty:
        issues.append(
            QualityIssue(
                code="duplicate_order_id",
                message="Order ID appears more than once.",
                rows=_row_numbers(duplicated),
            )
        )

    invalid_phone = normalized_orders[
        ~normalized_orders["phone"].astype(str).str.fullmatch(r"1\d{10}")
    ]
    if not invalid_phone.empty:
        issues.append(
            QualityIssue(
                code="invalid_phone",
                message="Phone value is not an 11-digit mainland China mobile number.",
                rows=_row_numbers(invalid_phone),
            )
        )

    known_skus = set(normalized_skus["sku"].astype(str))
    missing_sku = normalized_orders[~normalized_orders["sku"].astype(str).isin(known_skus)]
    if not missing_sku.empty:
        issues.append(
            QualityIssue(
                code="missing_sku",
                message="Order references a SKU that is not present in the SKU table.",
                rows=_row_numbers(missing_sku),
            )
        )

    negative_quantity = normalized_orders[normalized_orders["quantity"] < 0]
    if not negative_quantity.empty:
        issues.append(
            QualityIssue(
                code="negative_quantity",
                message="Order quantity is negative.",
                rows=_row_numbers(negative_quantity),
            )
        )

    missing_address = normalized_orders[
        normalized_orders["shipping_address"].isna()
        | (normalized_orders["shipping_address"].astype(str).str.strip() == "")
    ]
    if not missing_address.empty:
        issues.append(
            QualityIssue(
                code="missing_shipping_address",
                message="Shipping address is missing.",
                rows=_row_numbers(missing_address),
            )
        )

    if "order_date" in normalized_orders.columns:
        invalid_order_date = normalized_orders[
            pd.to_datetime(normalized_orders["order_date"], errors="coerce").isna()
            & (normalized_orders["order_date"].astype(str).str.strip() != "")
        ]
        if not invalid_order_date.empty:
            issues.append(
                QualityIssue(
                    code="invalid_order_date",
                    message="Order date cannot be parsed.",
                    rows=_row_numbers(invalid_order_date),
                )
            )

    duplicate_sku = normalized_skus[normalized_skus["sku"].duplicated(keep=False)]
    if not duplicate_sku.empty:
        issues.append(
            QualityIssue(
                code="duplicate_sku",
                message="SKU appears more than once in the SKU table.",
                rows=_row_numbers(duplicate_sku),
            )
        )

    negative_sku_cost = normalized_skus[normalized_skus["cost"] < 0]
    if not negative_sku_cost.empty:
        issues.append(
            QualityIssue(
                code="negative_sku_cost",
                message="SKU cost is negative.",
                rows=_row_numbers(negative_sku_cost),
            )
        )

    order_amounts = (
        positive_orders.groupby("order_id", as_index=True)["line_amount"].sum().to_dict()
    )
    known_order_ids = set(normalized_orders["order_id"].astype(str))
    refund_unknown_order = normalized_refunds[
        ~normalized_refunds["order_id"].astype(str).isin(known_order_ids)
    ]
    if not refund_unknown_order.empty:
        issues.append(
            QualityIssue(
                code="refund_unknown_order",
                message="Refund references an order that is not present in the order table.",
                rows=_row_numbers(refund_unknown_order),
            )
        )

    refund_exceeds = normalized_refunds[
        normalized_refunds.apply(
            lambda row: row["refund_amount"] > order_amounts.get(row["order_id"], 0),
            axis=1,
        )
    ]
    if not refund_exceeds.empty:
        issues.append(
            QualityIssue(
                code="refund_exceeds_order_amount",
                message="Refund amount is greater than the matched positive order amount.",
                rows=_row_numbers(refund_exceeds),
            )
        )

    return QualityReport(metrics=metrics, issues=issues)


def _row_numbers(frame: pd.DataFrame) -> list[int]:
    return [int(index) + 2 for index in frame.index]
