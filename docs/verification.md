# Verification Log

Last verified on 2026-06-24.

## Commands

```powershell
python -m pytest -q
python -m ruff check src tests
python -m pip_audit -r requirements.txt
cd frontend
npm audit --audit-level=low
npm run build
npm run e2e -- --reporter=line
cd ..
docker compose config
docker compose build
```

When network access to audit services is unstable, run the functional subset:

```powershell
.\scripts\verify.ps1 -SkipAudits
.\scripts\smoke-docker.ps1
```

## Latest Local Results

- `python -m pytest -q`: **21 passed**, 1 third-party multipart deprecation warning.
- `python -m ruff check src tests`: **passed**.
- `python -m pip_audit -r requirements.txt`: **passed**, no known vulnerabilities found.
- `npm audit --audit-level=low`: **passed**, 0 vulnerabilities.
- `npm run build`: **passed**.
- `npm run e2e -- --reporter=line`: **4 passed** in Chromium.
- `docker compose config`: **passed**.
- `docker compose build`: **passed**.
- `.\scripts\verify.ps1 -SkipAudits -SkipE2E`: **passed**.
- `.\scripts\smoke-docker.ps1`: **passed**.
- `.\scripts\start-dev.ps1 -FrontendPort 5174` and `.\scripts\stop-dev.ps1`: **passed**, services started, health checks passed, and ports were released.

## Browser Smoke Test

Local services used for verification:

- Backend: `http://127.0.0.1:8011`
- Frontend: `http://127.0.0.1:5179`

Verified with Playwright CLI:

- Page renders `ShopSheet`.
- Frontend loads live API data.
- KPI values render from `/api/demo-report`.
- Upload controls accept `examples/orders_messy.csv`, `examples/skus.csv`, and `examples/refunds.csv`.
- Clicking `Analyze uploads` displays `Uploaded files analyzed successfully.`
- Deliverable package section exposes downloads for clean orders, issue rows, and report.
- Missing required upload files show a readable preflight message.
- Bad order table headers show a readable API validation message.
- Oversized uploads show the HTTP 413 upload limit message.
- Screenshot saved to `docs/screenshots/shopsheet-workspace.png`.

## Docker Runtime Smoke Test

Runtime services used for verification:

- Backend: `http://127.0.0.1:18000`
- Frontend: `http://127.0.0.1:15173`

Commands:

```powershell
$env:SHOPSHEET_BACKEND_PORT="18000"
$env:SHOPSHEET_FRONTEND_PORT="15173"
docker compose --project-name shopsheet_verify up -d --build --force-recreate
```

Equivalent scripted check:

```powershell
.\scripts\smoke-docker.ps1
```

Observed results:

- `GET /health`: `{"status":"ok","service":"shopsheet"}`
- Frontend homepage: HTTP 200.
- Frontend proxy `GET /api/demo-report`: `orders=6`, `issues=7`, exports `clean_orders.csv|issue_rows.csv|quality_report.md`.
- Frontend proxy `GET /api/demo-export/issue_rows.csv`: CSV starts with `code,message,source_table,row`.

## Notes

- FastAPI currently emits a third-party `PendingDeprecationWarning` from Starlette multipart parsing during tests. It does not fail the test suite.
- Manual Docker checks can use project `shopsheet_verify`; `scripts/smoke-docker.ps1` uses project `shopsheet_smoke` by default and stops containers unless `-KeepRunning` is passed.
