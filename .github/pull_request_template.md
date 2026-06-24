## Summary

- 

## Verification

- [ ] `python -m pytest -q`
- [ ] `python -m ruff check src tests`
- [ ] `cd frontend && npm audit --audit-level=low`
- [ ] `cd frontend && npm run build`
- [ ] `cd frontend && npm run e2e -- --reporter=line`
- [ ] `docker compose config`
- [ ] `.\scripts\smoke-docker.ps1`

## Data Safety

- [ ] I used synthetic data only.
- [ ] I did not commit marketplace tokens, merchant exports, or customer data.
