from __future__ import annotations

from shopsheet.quality import QualityReport


def render_markdown_report(report: QualityReport) -> str:
    lines = [
        "# ShopSheet Quality Report",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Order rows | {report.metrics['order_rows']} |",
        f"| SKU rows | {report.metrics['sku_rows']} |",
        f"| Refund rows | {report.metrics['refund_rows']} |",
        f"| Gross sales | {report.metrics['gross_sales']:.2f} |",
        f"| Refund amount | {report.metrics['refund_amount']:.2f} |",
        f"| Estimated gross margin | {report.metrics['estimated_gross_margin']:.2f} |",
        "",
        (
            "Note: estimated gross margin is a rough estimate; unknown-cost SKUs are "
            "excluded from margin contribution, and refunds are deducted by total amount."
        ),
        "",
        "## Issues",
        "",
        "| Code | Count | Rows |",
        "|---|---:|---|",
    ]

    for issue in report.issues:
        rows = ", ".join(str(row) for row in issue.rows)
        lines.append(f"| {issue.code} | {len(issue.rows)} | {rows} |")

    return "\n".join(lines) + "\n"
