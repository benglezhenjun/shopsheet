# Changelog

## 0.1.0 - 2026-06-24

### Added

- Created ShopSheet as a local-first ecommerce spreadsheet quality workbench.
- Added order, SKU, and refund example datasets.
- Added Chinese-header example datasets for localized merchant exports.
- Added deterministic data quality checks for duplicate orders, invalid phones, missing SKU references, negative quantities, missing addresses, and refund mismatches.
- Added column normalization for common English and Chinese merchant exports.
- Added FastAPI endpoints for health checks, demo analysis, upload analysis, and demo exports.
- Added React/Vite operator workspace with KPI summary, upload flow, issue queue, order preview, and deliverable downloads.
- Added CSV/Markdown export package for clean orders, issue rows, and quality report.
- Added row-level `source_table` metadata to issue exports.
- Added upload handling for same-named files from different input roles.
- Added 5 MB per-file upload limit with HTTP 413 responses.
- Added browser E2E coverage for upload analysis, deliverable downloads, missing-file handling, bad-header validation, and oversized upload handling.
- Isolated browser E2E ports to avoid accidentally testing another local Vite app.
- Added scripted Docker runtime smoke verification.
- Added reliable local dev start/stop scripts with logs, PID metadata, health checks, and port cleanup.
- Added CI Docker runtime smoke coverage.
- Added Dependabot configuration for GitHub Actions, Python, and npm.
- Added showcase acceptance and release checklist documentation.
- Added CI workflow, Docker configuration, README, screenshots, issue templates, and verification notes.

### Verified

- Backend tests: 21 passed.
- Backend lint: passed.
- Python dependency audit: passed.
- Frontend dependency audit: passed.
- Frontend production build: passed.
- Browser E2E: 4 passed.
- Docker Compose config, build, and runtime smoke test: passed locally.

### Known Limitations

- Remote GitHub Actions results are pending until the repository is pushed.
- Upload result history is currently in-memory on the browser side.
- Inventory workflows are planned but not implemented yet.
