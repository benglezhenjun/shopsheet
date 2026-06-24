from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi import FastAPI, File, HTTPException, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

from shopsheet.exports import build_export_package
from shopsheet.pipeline import build_audit_bundle

MAX_UPLOAD_BYTES = 5 * 1024 * 1024

app = FastAPI(
    title="ShopSheet API",
    description="Spreadsheet quality API for small ecommerce merchant exports.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    # Localhost-only whitelist for the Vite operator workspace.
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["content-type"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "shopsheet"}


class Metrics(BaseModel):
    order_rows: int
    sku_rows: int
    refund_rows: int
    gross_sales: float
    refund_amount: float
    estimated_gross_margin: float
    clean_order_count: int
    excluded_order_count: int
    issue_count: int


class Issue(BaseModel):
    code: str
    message: str
    count: int
    rows: list[int]


class IssueRow(BaseModel):
    code: str
    message: str
    source_table: str
    row: int


class CleanOrder(BaseModel):
    order_id: str
    sku: str
    quantity: float
    unit_price: float
    phone: str
    shipping_address: str
    order_date: str
    line_amount: float
    estimated_line_margin: float


class AuditBundleResponse(BaseModel):
    metrics: Metrics
    issues: list[Issue]
    issue_rows: list[IssueRow]
    clean_orders: list[CleanOrder]
    markdown_report: str
    export_files: dict[str, str]


@app.get("/api/demo-report", response_model=AuditBundleResponse)
def demo_report() -> AuditBundleResponse:
    return _bundle_payload(_build_demo_bundle())


@app.get("/api/demo-export/{filename}")
def demo_export(filename: str) -> Response:
    package = build_export_package(_build_demo_bundle())
    if filename not in package.files:
        raise HTTPException(status_code=404, detail="Export file not found")

    media_type = "text/markdown" if filename.endswith(".md") else "text/csv"
    return Response(
        content=package.files[filename],
        media_type=f"{media_type}; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.post("/api/analyze", response_model=AuditBundleResponse)
async def analyze_uploads(
    order_file: UploadFile = File(...),
    sku_file: UploadFile = File(...),
    refund_file: UploadFile = File(...),
) -> AuditBundleResponse:
    with TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        order_path = await _save_upload(order_file, temp_root, "orders")
        sku_path = await _save_upload(sku_file, temp_root, "skus")
        refund_path = await _save_upload(refund_file, temp_root, "refunds")
        try:
            bundle = await run_in_threadpool(
                build_audit_bundle, order_path, sku_path, refund_path
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _bundle_payload(bundle)


async def _save_upload(upload: UploadFile, destination: Path, role: str) -> Path:
    suffix = Path(upload.filename or "upload.csv").suffix.lower() or ".csv"
    path = destination / f"{role}{suffix}"
    content = await upload.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail=f"{role} file exceeds 5 MB upload limit")
    path.write_bytes(content)
    return path


def _build_demo_bundle():
    root = Path(__file__).resolve().parents[2]
    return build_audit_bundle(
        order_path=root / "examples" / "orders_messy.csv",
        sku_path=root / "examples" / "skus.csv",
        refund_path=root / "examples" / "refunds.csv",
    )


def _bundle_payload(bundle) -> dict[str, object]:
    payload = asdict(bundle)
    payload["export_files"] = build_export_package(bundle).files
    return payload
