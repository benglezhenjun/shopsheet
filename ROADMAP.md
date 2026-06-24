# Roadmap

ShopSheet is focused on small ecommerce spreadsheet operations. The roadmap favors practical merchant workflows over broad SaaS scope.

## 0.1 Showcase Release

- Local order/SKU/refund analysis
- CSV/XLSX loading
- English and Chinese column normalization
- Data quality issue queue
- Clean order, issue row, and report exports
- React operator workspace
- FastAPI backend
- Browser E2E workflow
- CI, Docker configuration, local Docker runtime verification, and synthetic examples

## 0.2 Merchant Workflow Hardening

- More marketplace field aliases
- Inventory table support
- Per-upload export history
- Better remediation hints for each issue type
- More browser E2E scenarios for mobile layout, API fallback, and larger sample files

## 0.3 Operations Pack

- Batch folder processing
- Reusable validation profiles
- XLSX export with separate clean/issues/report sheets
- Optional local SQLite run history
- Release checklist and signed GitHub release notes

## Non-Goals

- Marketplace login or token management
- Payment processing
- Multi-tenant SaaS accounts
- Full ERP replacement
