from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from shopsheet.io import load_table
from shopsheet.mapping import normalize_orders, normalize_refunds, normalize_skus
from shopsheet.quality import analyze_shop_data
from shopsheet.reporting import render_markdown_report


@dataclass(frozen=True)
class AuditBundle:
    metrics: dict[str, float | int]
    issues: list[dict[str, object]]
    issue_rows: list[dict[str, object]]
    clean_orders: list[dict[str, object]]
    markdown_report: str


def build_audit_bundle(
    order_path: str | Path, sku_path: str | Path, refund_path: str | Path
) -> AuditBundle:
    orders = normalize_orders(load_table(order_path))
    skus = normalize_skus(load_table(sku_path))
    refunds = normalize_refunds(load_table(refund_path))
    report = analyze_shop_data(orders, skus, refunds)

    clean_orders = _build_clean_orders(orders, skus)
    issue_rows = [
        {
            "code": issue.code,
            "message": issue.message,
            "source_table": _source_table_for_issue(issue.code),
            "row": row,
        }
        for issue in report.issues
        for row in issue.rows
    ]
    issues = [
        {
            "code": issue.code,
            "message": issue.message,
            "count": len(issue.rows),
            "rows": issue.rows,
        }
        for issue in report.issues
    ]
    metrics = dict(report.metrics)
    metrics["issue_count"] = len(issue_rows)

    return AuditBundle(
        metrics=metrics,
        issues=issues,
        issue_rows=issue_rows,
        clean_orders=clean_orders,
        markdown_report=render_markdown_report(report),
    )


def _build_clean_orders(orders: pd.DataFrame, skus: pd.DataFrame) -> list[dict[str, object]]:
    sku_costs = skus.set_index("sku")["cost"].to_dict()
    output = orders.copy()
    output["line_amount"] = (output["quantity"] * output["unit_price"]).round(2)
    output["unit_cost"] = output["sku"].map(sku_costs).fillna(0)
    output["estimated_line_margin"] = (
        output["line_amount"] - output["quantity"] * output["unit_cost"]
    ).round(2)
    return output.to_dict("records")


def _source_table_for_issue(code: str) -> str:
    if code in {"duplicate_sku", "negative_sku_cost"}:
        return "skus"
    if code in {"refund_unknown_order", "refund_exceeds_order_amount"}:
        return "refunds"
    return "orders"
