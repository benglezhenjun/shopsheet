from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from shopsheet.economics import enrich_orders


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
    """Analyze merchant tables.

    estimated_gross_margin is a rough margin estimate: order rows with unknown SKU
    cost are excluded from margin contribution, and refunds are deducted by total
    refund amount.
    """
    normalized_orders = orders.copy()
    normalized_skus = skus.copy()
    normalized_refunds = refunds.copy()

    invalid_quantity = _invalid_numeric_rows(normalized_orders, "quantity")
    invalid_unit_price = _invalid_numeric_rows(normalized_orders, "unit_price")
    invalid_cost = _invalid_numeric_rows(normalized_skus, "cost")
    invalid_refund_amount = _invalid_numeric_rows(normalized_refunds, "refund_amount")

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

    enriched_orders = enrich_orders(normalized_orders, normalized_skus)
    positive_orders = enriched_orders[enriched_orders["quantity"] > 0].copy()
    known_margin_orders = positive_orders[positive_orders["unit_cost"].notna()]

    gross_sales = round(float(positive_orders["line_amount"].sum()), 2)
    refund_amount = round(float(normalized_refunds["refund_amount"].sum()), 2)
    gross_margin = round(
        float(known_margin_orders["estimated_line_margin"].sum()) - refund_amount,
        2,
    )

    metrics: dict[str, float | int] = {
        "order_rows": int(len(normalized_orders)),
        "sku_rows": int(len(normalized_skus)),
        "refund_rows": int(len(normalized_refunds)),
        "gross_sales": gross_sales,
        "refund_amount": refund_amount,
        "estimated_gross_margin": gross_margin,
    }

    issues: list[QualityIssue] = []

    if not invalid_quantity.empty:
        issues.append(
            QualityIssue(
                code="invalid_quantity",
                message="Order quantity cannot be parsed as a number.",
                rows=_row_numbers(invalid_quantity),
            )
        )

    if not invalid_unit_price.empty:
        issues.append(
            QualityIssue(
                code="invalid_unit_price",
                message="Order unit price cannot be parsed as a number.",
                rows=_row_numbers(invalid_unit_price),
            )
        )

    if not invalid_cost.empty:
        issues.append(
            QualityIssue(
                code="invalid_cost",
                message="SKU cost cannot be parsed as a number.",
                rows=_row_numbers(invalid_cost),
            )
        )

    if not invalid_refund_amount.empty:
        issues.append(
            QualityIssue(
                code="invalid_refund_amount",
                message="Refund amount cannot be parsed as a number.",
                rows=_row_numbers(invalid_refund_amount),
            )
        )

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
        ~_phone_strings(normalized_orders["phone"]).str.fullmatch(r"1\d{10}")
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
        positive_orders.assign(_order_id=positive_orders["order_id"].astype(str))
        .groupby("_order_id", as_index=True)["line_amount"]
        .sum()
        .to_dict()
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
            lambda row: (
                str(row["order_id"]) in order_amounts
                and row["refund_amount"] > order_amounts[str(row["order_id"])]
            ),
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


def _invalid_numeric_rows(frame: pd.DataFrame, column: str) -> pd.DataFrame:
    values = frame[column]
    parsed = pd.to_numeric(values, errors="coerce")
    nonempty = values.notna() & values.astype("string").str.strip().ne("")
    return frame[parsed.isna() & nonempty]


def _phone_strings(series: pd.Series) -> pd.Series:
    return series.map(_clean_phone_value)


def _clean_phone_value(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if text.endswith(".0") and text[:-2].isdigit():
        return text[:-2]
    return text
