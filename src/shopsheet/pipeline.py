from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from shopsheet.economics import enrich_orders
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

    dirty_order_indexes = {
        row - 2
        for issue in report.issues
        if _source_table_for_issue(issue.code) == "orders"
        for row in issue.rows
        if row >= 2
    }
    clean_orders = _build_clean_orders(orders, skus, dirty_order_indexes)
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
    metrics["clean_order_count"] = len(clean_orders)
    metrics["excluded_order_count"] = metrics["order_rows"] - len(clean_orders)
    metrics["issue_count"] = len(issue_rows)

    return AuditBundle(
        metrics=metrics,
        issues=issues,
        issue_rows=issue_rows,
        clean_orders=clean_orders,
        markdown_report=render_markdown_report(report),
    )


def _build_clean_orders(
    orders: pd.DataFrame, skus: pd.DataFrame, dirty_indexes: set[int]
) -> list[dict[str, object]]:
    output = enrich_orders(orders, skus)
    output = output.drop(index=dirty_indexes, errors="ignore").drop(
        columns=["unit_cost"], errors="ignore"
    )
    return output.to_dict("records")


def _source_table_for_issue(code: str) -> str:
    if code in {"duplicate_sku", "negative_sku_cost", "invalid_cost"}:
        return "skus"
    if code in {
        "invalid_refund_amount",
        "refund_unknown_order",
        "refund_exceeds_order_amount",
    }:
        return "refunds"
    return "orders"
