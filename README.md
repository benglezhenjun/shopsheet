# ShopSheet

ShopSheet is a local-first spreadsheet quality workbench for small ecommerce merchants. It turns exported order, SKU, and refund files into clean order rows, issue queues, and a reviewable business report.

## Why It Exists

Small merchants often reconcile marketplace exports in Excel before shipping, refund review, and margin checks. A few dirty rows can cause wrong shipments, mismatched refunds, or misleading profit numbers. ShopSheet makes that review repeatable.

## Current Product Slice

- Import order, SKU, and refund tables from CSV/XLSX.
- Normalize common English and Chinese merchant export headers.
- Detect duplicate orders, missing SKU references, invalid phone values, missing addresses, negative quantities, and refund mismatches.
- Calculate gross sales, refund amount, and estimated gross margin.
- Expose the analysis through a FastAPI backend.
- Provide a React operator workspace with KPI summary, issue queue, clean order preview, and upload flow.
- Download merchant deliverables: clean orders CSV, issue rows CSV, and Markdown quality report.
- Reject oversized uploads before table parsing to keep local runs predictable.

## Screenshot

![ShopSheet workspace](docs/screenshots/shopsheet-workspace.png)

## Quick Start

Backend:

```powershell
python -m pip install -e ".[dev]"
uvicorn shopsheet.api:app --reload --host 127.0.0.1 --port 8000
```

Frontend:

```powershell
cd frontend
npm ci
npm run dev
```

Open `http://127.0.0.1:5173`.

If port `8000` is already occupied, start the backend on another port and point Vite to it:

```powershell
$env:PYTHONPATH="src"
python -m uvicorn shopsheet.api:app --host 127.0.0.1 --port 8001

cd frontend
$env:VITE_API_PROXY="http://127.0.0.1:8001"
npm run dev -- --port 5173
```

Windows helper:

```powershell
.\scripts\start-dev.ps1
```

The helper writes local logs and process metadata under `.runtime/`. Stop the dev services with:

```powershell
.\scripts\stop-dev.ps1
```

## Validation

Backend tests:

```powershell
python -m pytest -q
python -m ruff check src tests
```

Frontend build and browser workflow:

```powershell
cd frontend
npm audit --audit-level=low
npm run build
npm run e2e -- --reporter=line
```

Full local verification script:

```powershell
.\scripts\verify.ps1
```

If your network blocks PyPI, OSV, or npm audit endpoints, run the functional checks first:

```powershell
.\scripts\verify.ps1 -SkipAudits
```

Docker runtime:

```powershell
cd frontend
npm run build
cd ..
$env:SHOPSHEET_BACKEND_PORT="18000"
$env:SHOPSHEET_FRONTEND_PORT="15173"
docker compose config
docker compose up -d --build
```

Open `http://127.0.0.1:15173` for the Docker-served frontend.

Scripted Docker smoke test:

```powershell
.\scripts\smoke-docker.ps1
```

## API

- `GET /health`
- `GET /api/demo-report`
- `GET /api/demo-export/{filename}`
- `POST /api/analyze`

`POST /api/analyze` expects multipart files named:

- `order_file`
- `sku_file`
- `refund_file`

Each uploaded file is limited to 5 MB in the local showcase build.

Demo export filenames:

- `clean_orders.csv`
- `issue_rows.csv`
- `quality_report.md`

## Example Data

Synthetic merchant files live in `examples/`:

- `orders_messy.csv`
- `skus.csv`
- `refunds.csv`
- `orders_chinese_headers.csv`
- `skus_chinese_headers.csv`
- `refunds_chinese_headers.csv`

They are safe to publish and designed to trigger realistic quality issues.

## Project Structure

```text
src/shopsheet/        Python data core and FastAPI app
tests/                Backend behavior tests
examples/             Synthetic merchant exports
frontend/             React/Vite operator workspace
docs/                 Product brief and implementation plans
.github/workflows/    CI checks
```

## Project Maturity

- [Showcase acceptance](docs/showcase-acceptance.md)
- [Completion ladder](docs/completion-ladder.md)
- [Verification log](docs/verification.md)
- [Release checklist](docs/release-checklist.md)
- [Architecture](docs/architecture.md)
- [Roadmap](ROADMAP.md)

## Non-Goals

ShopSheet is not a full ERP, payment system, marketplace authorization layer, or multi-tenant SaaS. The project stays focused on a polished, testable spreadsheet operations workflow.

## Safety

Do not commit real merchant exports, customer data, marketplace tokens, or payment credentials. The repository uses synthetic data only.
