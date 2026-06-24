# Architecture

ShopSheet separates deterministic spreadsheet logic from transport and UI layers.

## Layers

```text
React workspace
  -> FastAPI endpoints
    -> audit pipeline
      -> table loading
      -> column mapping
      -> quality rules
      -> export package
```

## Python Core

- `shopsheet.io` loads CSV/XLSX tables.
- `shopsheet.mapping` maps merchant export headers into canonical columns.
- `shopsheet.quality` calculates metrics and rule violations.
- `shopsheet.pipeline` builds a complete audit bundle.
- `shopsheet.exports` renders merchant deliverables.
- `shopsheet.api` exposes the workflow through FastAPI.

The core is intentionally independent from the web UI so rules can be tested without a browser.

## Frontend

The React app is an operator workspace:

- Upload order, SKU, and refund files.
- Review KPI summary and issue queue.
- Preview clean order rows.
- Download clean orders, issue rows, and quality report.

## Data Flow

1. User uploads three merchant files.
2. API rejects files over 5 MB, then stores accepted files in a temporary directory for the request.
3. Pipeline loads and normalizes each table.
4. Quality rules produce metrics and row-level issues.
5. Export package generates CSV and Markdown deliverables.
6. Frontend displays the audit bundle and downloads deliverables from the current result.

## Design Tradeoffs

- No database yet: keeps the portfolio slice simple and reproducible.
- No marketplace API: avoids credential risk and keeps the project open-source friendly.
- CSV/Markdown first: proves business value before adding richer XLSX exports.
- 5 MB upload limit: keeps the local-first demo predictable before adding streaming or background jobs.
