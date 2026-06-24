# ShopSheet Polished Product Roadmap

> **For Codex:** REQUIRED SUB-SKILL: Use test-driven-development for backend behavior and frontend-skill for the product UI. Do not use subagents unless the user explicitly allows them.

**Goal:** Turn ShopSheet from a tested data core into a polished open-source portfolio product for small ecommerce spreadsheet operations.

**Architecture:** Keep deterministic data rules in `src/shopsheet`, expose them through a thin FastAPI app, and build a React/Vite operator workspace around the sample workflow. The UI should be dense, operational, and product-like rather than a marketing page.

**Tech Stack:** Python 3.12, pandas, FastAPI, pytest, React, Vite, CSS, GitHub Actions, Docker.

---

## Product Definition

ShopSheet helps small ecommerce merchants inspect platform-exported order, SKU, and refund spreadsheets before shipping, reconciliation, and margin review.

## Polished Acceptance Criteria

- A non-technical reviewer can open the project and understand the product in under 60 seconds.
- The repository has synthetic example data and a repeatable demo flow.
- The backend can load, normalize, validate, summarize, and render report data.
- The API exposes health and demo-analysis endpoints.
- The frontend presents the working surface: KPI summary, issue queue, table preview, and export/report affordances.
- Tests cover core business rules and API behavior.
- README includes product positioning, screenshots or screenshot instructions, setup, test, and run commands.
- CI runs backend tests and frontend build.
- Docker Compose can start the app stack or, if not fully validated locally, the limitation is documented.

## Visual Thesis

Quiet operations desk: white workspace, crisp spreadsheet density, restrained dark text, one green action accent, and clear risk markers.

## Content Plan

- Workspace header: product name, current demo dataset, primary run/export actions.
- KPI strip: order rows, gross sales, refunds, margin, issue count.
- Main work area: issue queue and order preview.
- Inspector: report summary and next actions for a merchant operator.

## Interaction Thesis

- Subtle first-load reveal for summary and issue queue.
- Hover states on issue rows and action buttons.
- Sticky right inspector so the report context stays visible while reviewing rows.

## Implementation Tasks

### Task 1: Normalize Merchant Columns

Add a mapping layer that converts common English and Chinese merchant export headers into canonical ShopSheet columns.

### Task 2: Build Audit Bundle

Create a pipeline that loads order, SKU, and refund files, normalizes columns, runs analysis, and returns metrics, issues, clean rows, and Markdown report text.

### Task 3: FastAPI App

Expose `/health`, `/api/demo-report`, and later `/api/analyze` upload endpoints.

### Task 4: React Operator Workspace

Build a Vite app with a production-like ecommerce data review surface using the demo report endpoint and resilient fallback sample data.

### Task 5: Repository Polish

Add CI, Docker files, expanded README, license, and contribution notes.

### Task 6: Verification

Run backend tests, frontend build, API smoke checks, and browser screenshot verification before marking the product polished.
