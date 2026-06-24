# ShopSheet Product Brief

## Target User

Small ecommerce merchants and operators who export order, SKU, and refund spreadsheets from marketplaces, then reconcile them manually in Excel.

## Core Problem

Spreadsheet errors directly affect shipping, refund reconciliation, margin review, and inventory decisions. The user needs fast, local, repeatable checks before using those files for operations.

## V1 Goal

Given order, SKU, and refund tables, ShopSheet should identify common data issues and calculate a business summary that a non-technical merchant can inspect.

## V1 Non-Goals

- Marketplace API authorization
- Payment processing
- Multi-tenant SaaS accounts
- Full ERP workflows
- Real customer data ingestion in the repository

## Acceptance Criteria

- Example CSV files are included and synthetic.
- Core quality rules are covered by automated tests.
- The analysis core is independent from the future web layer.
- `python -m pytest -q` passes from the repository root.
- The README explains scope and local validation clearly.
