# ShopSheet Completion Ladder

Last assessed: 2026-06-24

## Current Score

Current local completion: **94%**

ShopSheet is no longer a basic demo. It has a tested data core, FastAPI backend, React operator workspace, sample data, CI configuration, Docker images, issue templates, download-ready deliverables, scripted browser E2E coverage, upload boundary protection, Docker runtime smoke evidence, Dependabot configuration, and explicit showcase/release acceptance checklists.

It is not yet a 95% open-source showcase because the repository has not been committed, pushed to GitHub, or validated by remote GitHub Actions.

## Five Levels

### Level 1: 20% Prototype Skeleton

The repository has product positioning, a dedicated project folder, synthetic sample data, and a minimal runnable shape.

Acceptance checks:
- [x] Product brief exists.
- [x] Example files are synthetic.
- [x] README explains the intended user and workflow.

### Level 2: 40% Tested Data Core

The project can load merchant tables, normalize columns, detect core data issues, calculate summary metrics, and generate a report through tested Python code.

Acceptance checks:
- [x] `python -m pytest -q` passes.
- [x] Core rules have behavior tests.
- [x] Data logic is independent from the web layer.

### Level 3: 60% Usable Demo MVP

The project has a working local web experience that a reviewer can open, use with sample files, and understand without reading source code.

Acceptance checks:
- [x] Backend API exposes health, demo report, and upload analysis.
- [x] Frontend shows KPI summary, issue queue, order preview, and upload flow.
- [x] Browser smoke test verifies the workflow.
- [x] Screenshot exists in docs.

### Level 4: 80% Merchant-Deliverable Tool

The project produces useful deliverables after analysis: clean order data, issue rows, and a report package. Upload failures and operator next steps are clear.

Acceptance checks:
- [x] API can return/export clean orders as CSV.
- [x] API can return/export issue rows as CSV.
- [x] API can return/export Markdown report.
- [x] Frontend has real download actions for each deliverable.
- [x] Tests cover export data shape and API behavior.
- [x] Uploads reject oversized files with HTTP 413.

### Level 5: 95% Open-Source Showcase

The project is ready to pin on GitHub and use in a portfolio. It has stable CI, Docker runtime verification, polished docs, issue templates, release notes, and end-to-end workflow evidence.

Acceptance checks:
- [x] CI covers backend tests, linting, dependency audits, frontend build, Docker build, and browser E2E.
- [x] Docker Compose runtime is verified locally.
- [x] Docker runtime smoke is scripted locally and represented in CI.
- [x] README includes screenshots, demo flow, commands, architecture, and roadmap.
- [x] GitHub issue templates exist.
- [x] Dependabot is configured for GitHub Actions, Python, and npm.
- [x] End-to-end browser test is documented and passes locally.
- [x] Dependency audits pass locally.
- [ ] First remote GitHub Actions run passes after push.
- [ ] A release tag or pinned showcase commit exists.

## Next Upgrade Target

Move from **94%** to **95%** by completing the publication gate:

- Commit the current repository after user confirmation.
- Push to GitHub and let the first CI run prove the workflow remotely.
- Add the CI badge once the repository URL is known.
- Create a `v0.1.0` tag or GitHub release with the screenshot and verification summary.

## Progress Update

The 80%-to-94% upgrade slice is implemented:

- `clean_orders.csv` export
- `issue_rows.csv` export
- `quality_report.md` export
- `/api/demo-export/{filename}` endpoint
- Frontend deliverable download section
- Backend tests for export package and API behavior
- Uploaded analyses now return `export_files`, so frontend downloads can use the current analysis result rather than only demo exports.
- Upload validation errors now return HTTP 400 with readable missing-column details, and the frontend displays those details.
- Same-named upload files no longer overwrite each other inside the temporary request directory.
- Oversized uploads are rejected with HTTP 413 before table parsing.
- Browser E2E verifies upload, all three downloads, missing-file handling, bad-header handling, and oversized upload handling.
- Synthetic Chinese-header examples prove localized merchant exports through the same pipeline.
- Docker Compose runtime has been rebuilt and smoke-tested locally.
- Docker runtime smoke is available as `scripts/smoke-docker.ps1`.
- CI now includes Docker runtime smoke, not only image build.
- Showcase acceptance and release checklist docs define how to verify the GitHub portfolio target.
- Dependabot is configured for dependency maintenance after publication.
