# Changelog

All notable changes to ShopSheet are documented here. This project adheres to [Semantic Versioning](https://semver.org/).

## 1.0.0 - 2026-06-24

First public release.

### Features

- Import order, SKU, and refund tables from CSV (UTF-8 and GB18030) or XLSX, keeping identifier columns as text so zero-padded SKUs are not corrupted.
- Normalize common English and Simplified Chinese merchant export headers into canonical columns.
- Deterministic data-quality checks: duplicate orders, invalid mainland-China mobile numbers, missing SKU references, negative quantities, missing addresses, unparseable order dates, unparseable numeric cells (quantity, unit price, SKU cost, refund amount), duplicate SKUs, negative SKU cost, refunds against unknown orders, and refunds exceeding the matched order amount.
- `clean_orders.csv` contains only order rows that passed every quality check, with calculated line amount and estimated margin columns; `clean_order_count` and `excluded_order_count` are reported alongside the other metrics.
- `estimated_gross_margin` excludes order rows with unknown SKU cost from the margin contribution; the estimation rule is documented in the API docstring, the report, and the README.
- Merchant deliverables: `clean_orders.csv`, `issue_rows.csv` (one row per detected issue and source row, with `source_table` metadata), and `quality_report.md`.
- FastAPI backend with typed Pydantic response models, a 5 MB per-file upload limit (HTTP 413), localhost-scoped CORS, and threadpool-offloaded analysis.
- Simplified Chinese React/Vite operator workspace: KPI summary, issue queue with localized labels, clean order preview, upload flow, and deliverable downloads.

### Tooling

- Backend tests (pytest) with coverage gating, ruff lint, and pip-audit.
- Playwright browser E2E on isolated ports, covering upload analysis, deliverable downloads, the missing-file guard, bad-header validation, and oversized uploads.
- CI (GitHub Actions) for backend, frontend, Docker runtime smoke, and E2E; Dependabot for GitHub Actions, pip, and npm.
- Docker Compose runtime and Windows dev/verify helper scripts. Cross-platform (bash and PowerShell) commands documented in the README.

### Known Limitations

- Upload result history is in-memory in the browser only.
- Inventory workflows are planned but not yet implemented.
- Local-first by design: no authentication, multi-tenancy, or internet-facing hardening.
