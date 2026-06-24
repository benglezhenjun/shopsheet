from __future__ import annotations

from dataclasses import dataclass
from io import StringIO

import pandas as pd

from shopsheet.pipeline import AuditBundle


@dataclass(frozen=True)
class ExportPackage:
    files: dict[str, str]


def build_export_package(bundle: AuditBundle) -> ExportPackage:
    return ExportPackage(
        files={
            "clean_orders.csv": _records_to_csv(bundle.clean_orders),
            "issue_rows.csv": _records_to_csv(bundle.issue_rows),
            "quality_report.md": bundle.markdown_report,
        }
    )


def _records_to_csv(records: list[dict[str, object]]) -> str:
    buffer = StringIO()
    pd.DataFrame(records).to_csv(buffer, index=False)
    return buffer.getvalue()
