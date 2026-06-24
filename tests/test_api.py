from io import BytesIO

from fastapi.testclient import TestClient

from shopsheet.api import app


def test_health_endpoint_returns_ok():
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "shopsheet"}


def test_demo_report_endpoint_returns_bundle():
    client = TestClient(app)

    response = client.get("/api/demo-report")

    assert response.status_code == 200
    payload = response.json()
    assert payload["metrics"]["order_rows"] == 6
    assert payload["metrics"]["clean_order_count"] == 1
    assert payload["metrics"]["excluded_order_count"] == 5
    assert payload["metrics"]["issue_count"] == 7
    assert payload["issues"][0]["code"] == "duplicate_order_id"
    assert payload["clean_orders"][0]["order_id"] == "O-1001"
    assert "# ShopSheet Quality Report" in payload["markdown_report"]


def test_openapi_documents_audit_bundle_response_models():
    client = TestClient(app)

    payload = client.get("/openapi.json").json()

    schemas = payload["components"]["schemas"]
    assert "AuditBundleResponse" in schemas
    assert "Metrics" in schemas
    assert "Issue" in schemas
    assert "CleanOrder" in schemas
    assert payload["paths"]["/api/demo-report"]["get"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"]["$ref"].endswith("/AuditBundleResponse")
    assert payload["paths"]["/api/analyze"]["post"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"]["$ref"].endswith("/AuditBundleResponse")


def test_cors_preflight_is_limited_to_localhost_get_and_post():
    client = TestClient(app)

    rejected = client.options(
        "/api/analyze",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "DELETE",
        },
    )
    allowed = client.options(
        "/api/analyze",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert rejected.status_code == 400
    assert allowed.status_code == 200
    assert allowed.headers["access-control-allow-methods"] == "GET, POST"
    assert "access-control-allow-credentials" not in allowed.headers


def test_analyze_endpoint_accepts_uploaded_tables():
    client = TestClient(app)

    with (
        open("examples/orders_messy.csv", "rb") as order_file,
        open("examples/skus.csv", "rb") as sku_file,
        open("examples/refunds.csv", "rb") as refund_file,
    ):
        response = client.post(
            "/api/analyze",
            files={
                "order_file": ("orders_messy.csv", order_file, "text/csv"),
                "sku_file": ("skus.csv", sku_file, "text/csv"),
                "refund_file": ("refunds.csv", refund_file, "text/csv"),
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["metrics"]["order_rows"] == 6
    assert payload["metrics"]["clean_order_count"] == 1
    assert payload["metrics"]["issue_count"] == 7
    assert payload["issue_rows"][0]["code"] == "duplicate_order_id"
    assert set(payload["export_files"]) == {
        "clean_orders.csv",
        "issue_rows.csv",
        "quality_report.md",
    }
    assert payload["export_files"]["clean_orders.csv"].startswith(
        "order_id,sku,quantity,unit_price"
    )


def test_analyze_endpoint_builds_bundle_in_threadpool(monkeypatch):
    called = False

    async def fake_threadpool(func, *args, **kwargs):
        nonlocal called
        called = True
        return func(*args, **kwargs)

    monkeypatch.setattr("shopsheet.api.run_in_threadpool", fake_threadpool, raising=False)
    client = TestClient(app)

    with (
        open("examples/orders_messy.csv", "rb") as order_file,
        open("examples/skus.csv", "rb") as sku_file,
        open("examples/refunds.csv", "rb") as refund_file,
    ):
        response = client.post(
            "/api/analyze",
            files={
                "order_file": ("orders_messy.csv", order_file, "text/csv"),
                "sku_file": ("skus.csv", sku_file, "text/csv"),
                "refund_file": ("refunds.csv", refund_file, "text/csv"),
            },
        )

    assert response.status_code == 200
    assert called is True


def test_demo_export_endpoint_downloads_clean_orders_csv():
    client = TestClient(app)

    response = client.get("/api/demo-export/clean_orders.csv")

    assert response.status_code == 200
    assert response.headers["content-disposition"] == (
        'attachment; filename="clean_orders.csv"'
    )
    assert response.text.startswith("order_id,sku,quantity,unit_price")
    assert "O-1001,SKU-RED-M,2,79.9" in response.text
    assert "SKU-MISSING" not in response.text


def test_demo_export_endpoint_rejects_unknown_file():
    client = TestClient(app)

    response = client.get("/api/demo-export/not-real.csv")

    assert response.status_code == 404
    assert response.json()["detail"] == "Export file not found"


def test_analyze_endpoint_returns_readable_validation_error(tmp_path):
    client = TestClient(app)
    bad_orders = tmp_path / "bad_orders.csv"
    bad_orders.write_text("订单编号\nO-1001\n", encoding="utf-8")

    with (
        open(bad_orders, "rb") as order_file,
        open("examples/skus.csv", "rb") as sku_file,
        open("examples/refunds.csv", "rb") as refund_file,
    ):
        response = client.post(
            "/api/analyze",
            files={
                "order_file": ("bad_orders.csv", order_file, "text/csv"),
                "sku_file": ("skus.csv", sku_file, "text/csv"),
                "refund_file": ("refunds.csv", refund_file, "text/csv"),
            },
        )

    assert response.status_code == 400
    assert "Missing required order columns" in response.json()["detail"]


def test_analyze_endpoint_handles_same_uploaded_filenames():
    client = TestClient(app)

    with (
        open("examples/orders_messy.csv", "rb") as order_file,
        open("examples/skus.csv", "rb") as sku_file,
        open("examples/refunds.csv", "rb") as refund_file,
    ):
        response = client.post(
            "/api/analyze",
            files=[
                ("order_file", ("upload.csv", order_file, "text/csv")),
                ("sku_file", ("upload.csv", sku_file, "text/csv")),
                ("refund_file", ("upload.csv", refund_file, "text/csv")),
            ],
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["metrics"]["order_rows"] == 6
    assert payload["metrics"]["clean_order_count"] == 1
    assert payload["metrics"]["sku_rows"] == 3
    assert payload["metrics"]["refund_rows"] == 2


def test_analyze_endpoint_rejects_oversized_uploads():
    client = TestClient(app)
    too_large = b"not_order_column\n" + (b"x\n" * ((5 * 1024 * 1024) // 2 + 1))

    with (
        open("examples/skus.csv", "rb") as sku_file,
        open("examples/refunds.csv", "rb") as refund_file,
    ):
        response = client.post(
            "/api/analyze",
            files={
                "order_file": ("orders.csv", BytesIO(too_large), "text/csv"),
                "sku_file": ("skus.csv", sku_file, "text/csv"),
                "refund_file": ("refunds.csv", refund_file, "text/csv"),
            },
        )

    assert response.status_code == 413
    assert response.json()["detail"] == "orders file exceeds 5 MB upload limit"
