# Contributing

ShopSheet is intentionally small and focused. Contributions should improve the merchant spreadsheet workflow without turning the project into a full ERP.

## Development Checks

Install backend development dependencies (any OS):

```bash
python -m pip install -e ".[dev]"
```

Run backend tests (any OS):

```bash
python -m pytest -q
python -m ruff check src tests
python -m pip_audit -r requirements.txt
```

Run frontend checks (any OS):

```bash
cd frontend
npm ci
npm audit --audit-level=high
npm run build
npm run e2e -- --reporter=line
```

Run Docker runtime smoke when Docker Desktop is available (Windows helper):

```powershell
.\scripts\smoke-docker.ps1
```

## Scope Rules

- Keep data rules deterministic and test-first.
- Use synthetic data only.
- Do not commit real merchant files, credentials, or marketplace tokens.
- Prefer small vertical workflows over broad platform abstractions.
