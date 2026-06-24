from shopsheet.quality import QualityIssue, QualityReport
from shopsheet.reporting import render_markdown_report


def test_render_markdown_report_includes_metrics_and_issue_counts():
    report = QualityReport(
        metrics={
            "order_rows": 6,
            "sku_rows": 3,
            "refund_rows": 2,
            "gross_sales": 626.50,
            "refund_amount": 100.00,
            "estimated_gross_margin": 271.50,
        },
        issues=[
            QualityIssue(
                code="duplicate_order_id",
                message="Order ID appears more than once.",
                rows=[4, 5],
            ),
            QualityIssue(
                code="invalid_phone",
                message="Phone value is invalid.",
                rows=[3],
            ),
        ],
    )

    markdown = render_markdown_report(report)

    assert "# ShopSheet Quality Report" in markdown
    assert "| Gross sales | 626.50 |" in markdown
    assert "| Estimated gross margin | 271.50 |" in markdown
    assert "| duplicate_order_id | 2 | 4, 5 |" in markdown
    assert "| invalid_phone | 1 | 3 |" in markdown
