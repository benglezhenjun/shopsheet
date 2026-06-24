# Contributing

ShopSheet is intentionally small and focused. Contributions should improve the merchant spreadsheet workflow without turning the project into a full ERP.

## Development Checks

Install backend development dependencies:

```powershell
python -m pip install -e ".[dev]"
```

Run backend tests:

```powershell
python -m pytest -q
python -m ruff check src tests
python -m pip_audit -r requirements.txt
```

Run frontend checks:

```powershell
cd frontend
npm ci
npm audit --audit-level=low
npm run build
npm run e2e -- --reporter=line
```

Run Docker runtime smoke when Docker Desktop is available:

```powershell
.\scripts\smoke-docker.ps1
```

## Scope Rules

- Keep data rules deterministic and test-first.
- Use synthetic data only.
- Do not commit real merchant files, credentials, or marketplace tokens.
- Prefer small vertical workflows over broad platform abstractions.
