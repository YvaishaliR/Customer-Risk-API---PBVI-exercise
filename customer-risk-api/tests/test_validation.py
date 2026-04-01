import httpx
import pytest

BASE_URL = "http://localhost:8000"

LEAK_STRINGS = [
    "SELECT", "DROP", "TABLE", "INSERT", "UPDATE", "DELETE",
    "risk_profiles", "psycopg2", "Traceback", "Exception",
    "OperationalError", "SyntaxError",
]


def get(path, api_key):
    with httpx.Client(base_url=BASE_URL) as client:
        return client.get(path, headers={"X-API-Key": api_key})


def assert_no_internal_detail(resp):
    text = resp.text
    for term in LEAK_STRINGS:
        assert term not in text, f"Response leaks {term!r}: {text!r}"


def test_empty_id_returns_404(api_key):
    # No route registered for /api/v1/customers/ — expect 404
    resp = get("/api/v1/customers/", api_key)
    assert resp.status_code == 404


def test_lowercase_id_returns_422(api_key):
    resp = get("/api/v1/customers/demo-001", api_key)
    assert resp.status_code == 422
    assert_no_internal_detail(resp)


def test_overlength_id_returns_422(api_key):
    resp = get("/api/v1/customers/ABCDEFGHIJKLMNOPQRSTU", api_key)  # 21 chars
    assert resp.status_code == 422
    assert_no_internal_detail(resp)


def test_sql_injection_returns_422(api_key):
    resp = get("/api/v1/customers/DEMO-001'--", api_key)
    assert resp.status_code == 422
    assert_no_internal_detail(resp)


def test_semicolon_returns_422(api_key):
    resp = get("/api/v1/customers/DEMO-001;DROP TABLE", api_key)
    assert resp.status_code == 422
    assert_no_internal_detail(resp)


def test_422_body_no_internal_detail(api_key):
    invalid_ids = [
        "demo-001",
        "ABCDEFGHIJKLMNOPQRSTU",
        "DEMO-001'--",
        "DEMO-001;DROP TABLE",
    ]
    for customer_id in invalid_ids:
        resp = get(f"/api/v1/customers/{customer_id}", api_key)
        assert resp.status_code == 422, f"{customer_id!r} did not return 422"
        assert_no_internal_detail(resp)
