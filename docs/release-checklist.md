# Release Checklist

Use this before publishing ShopSheet as a GitHub showcase project.

## Local Preflight

```powershell
git status --short
python -m pytest -q
python -m ruff check src tests
cd frontend
npm ci
npm run build
npm run e2e -- --reporter=line
cd ..
.\scripts\smoke-docker.ps1
```

Run dependency audits when the network can reach PyPI, OSV, and npm:

```powershell
python -m pip_audit -r requirements.txt
cd frontend
npm audit --audit-level=low
cd ..
```

## Data Safety

- Check staged files with `git status --short`.
- Do not stage real merchant exports, customer rows, marketplace tokens, logs, or local secrets.
- Keep `examples/` synthetic.
- Keep generated folders such as `frontend/dist/`, `frontend/test-results/`, and caches ignored.

## GitHub Publication

```powershell
git add .
git commit -m "Initial ShopSheet showcase release"
git remote add origin <repo-url>
git push -u origin main
```

After push:

- Confirm all GitHub Actions jobs pass.
- Add a CI badge to `README.md` using the real repository URL.
- Create a `v0.1.0` tag or GitHub release.
- Attach or reference the screenshot from `docs/screenshots/shopsheet-workspace.png`.

## 95% Gate

The project reaches the 95% showcase target only after local verification and remote GitHub Actions both pass.
