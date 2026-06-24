# ShopSheet Implementation Plan

> **For Codex:** REQUIRED SUB-SKILL: Use test-driven-development to implement this plan task-by-task. Do not use subagents unless the user explicitly allows them.

**Goal:** Build the first production-quality slice of ShopSheet, a local-first data workbench for small ecommerce merchants to clean order, SKU, and refund spreadsheets and produce actionable quality and business reports.

**Architecture:** Start with a Python domain core that accepts tabular rows and returns deterministic validation findings plus summary metrics. Keep this core independent from FastAPI and the frontend so rules can be tested directly and later exposed through an API.

**Tech Stack:** Python 3.12, pandas, pytest, CSV/XLSX via pandas/openpyxl. Later phases add FastAPI, SQLite, React/Vite, and Docker Compose.

---

### Task 1: Project Skeleton And Product Contract

**Files:**
- Create: `README.md`
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `docs/product-brief.md`
- Create: `examples/orders_messy.csv`
- Create: `examples/skus.csv`
- Create: `examples/refunds.csv`

**Steps:**
1. Write the README with product positioning, first-stage scope, and local validation commands.
2. Add Python package metadata and pytest configuration.
3. Add example merchant CSV files with realistic dirty data.
4. Add a product brief describing users, non-goals, and V1 acceptance criteria.
5. Run `git status --short` to verify only ShopSheet files are affected.

### Task 2: Domain Models And Validation Report

**Files:**
- Create: `tests/test_quality_report.py`
- Create: `src/shopsheet/__init__.py`
- Create: `src/shopsheet/quality.py`

**Step 1: Write the failing test**

Test behavior:
- Given order, SKU, and refund rows, `analyze_shop_data()` returns a report object.
- The report includes row counts, total gross amount, total refund amount, and estimated gross margin.
- It flags duplicate order IDs, missing SKU references, refund amounts greater than order amount, invalid phone values, missing shipping address, and negative quantity.

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_quality_report.py -q`

Expected: `ModuleNotFoundError` or missing `analyze_shop_data`.

**Step 3: Write minimal implementation**

Implement `analyze_shop_data(orders, skus, refunds)` in `src/shopsheet/quality.py` using pandas.

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_quality_report.py -q`

Expected: all tests pass.

### Task 3: CSV Loader

**Files:**
- Create: `tests/test_io.py`
- Create: `src/shopsheet/io.py`

**Step 1: Write the failing test**

Test behavior:
- `load_table(path)` reads CSV and XLSX files into pandas data frames.
- Unsupported suffixes raise a clear `ValueError`.

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_io.py -q`

Expected: missing module or function.

**Step 3: Write minimal implementation**

Implement suffix-based CSV/XLSX loading.

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_io.py -q`

Expected: all tests pass.

### Task 4: Report Export

**Files:**
- Create: `tests/test_report_export.py`
- Create: `src/shopsheet/reporting.py`

**Step 1: Write the failing test**

Test behavior:
- A quality report can be rendered to Markdown with key metrics and issue counts.

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_report_export.py -q`

Expected: missing module or function.

**Step 3: Write minimal implementation**

Implement `render_markdown_report(report)`.

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_report_export.py -q`

Expected: all tests pass.

### Task 5: Verification Gate

**Files:**
- Modify: `README.md`

**Steps:**
1. Run `python -m pytest -q`.
2. Run `git status --short`.
3. Update README if commands or paths differ from reality.
4. Do not commit unless the user confirms.
