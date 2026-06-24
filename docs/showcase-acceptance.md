# Showcase Acceptance

This checklist defines how to judge whether ShopSheet is ready to pin as a GitHub portfolio project.

## Product Acceptance

- A reviewer can understand the target user from `README.md` within one minute.
- A reviewer can run the backend and frontend locally with documented commands.
- The sample data is synthetic and produces realistic ecommerce data issues.
- English and Chinese header examples both run through the same pipeline.
- The UI supports the complete core workflow:
  - load demo analysis,
  - upload order, SKU, and refund files,
  - review KPI values,
  - review issue rows,
  - preview clean orders,
  - download clean orders, issue rows, and Markdown report.
- Upload errors are readable to an operator.
- Oversized files fail fast with HTTP 413.

## Engineering Acceptance

- `python -m pytest -q` passes.
- `python -m ruff check src tests` passes.
- `cd frontend && npm run build` passes.
- `cd frontend && npm run e2e -- --reporter=line` passes.
- `.\scripts\smoke-docker.ps1` passes on a machine with Docker Desktop running.
- CI runs backend tests, lint, dependency audits, frontend build, Docker build, Docker runtime smoke, and browser E2E.

## Open-Source Acceptance

- `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md`, issue templates, and PR template exist.
- `CHANGELOG.md` describes the first showcase release.
- `docs/verification.md` records the latest local evidence and any unverifiable external checks.
- No real merchant data, credentials, local logs, or generated test artifacts are staged.
- A GitHub remote exists.
- The first remote GitHub Actions run passes.
- A `v0.1.0` tag or GitHub release exists.

## Current Verdict

Local acceptance is strong enough for a release candidate. The remaining 95% gate is publication evidence: first commit, GitHub remote, remote CI, and release/tag.
