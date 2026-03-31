import time

import docker
import httpx
import pytest

from app.db import get_conn, release_conn

BASE_URL = "http://localhost:8000"
POSTGRES_CONTAINER = "customer-risk-api-postgres-1"

LEAK_STRINGS = [
    "psycopg2", "Traceback", "postgres", "riskdb", "risk_profiles",
    "SELECT", "Exception", "Postgres", "POSTGRES_",
]


def http_get(path, api_key=None):
    headers = {"X-API-Key": api_key} if api_key else {}
    with httpx.Client(base_url=BASE_URL) as client:
        return client.get(path, headers=headers)


def db_snapshot(conn):
    cur = conn.cursor()
    cur.execute(
        "SELECT customer_id, risk_tier, array_to_string(risk_factors, ',') "
        "FROM risk_profiles ORDER BY customer_id"
    )
    return frozenset(cur.fetchall())


@pytest.fixture(scope="module")
def conn():
    c = get_conn()
    yield c
    try:
        release_conn(c)
    except Exception:
        pass


def test_no_write_on_200(conn, api_key):
    before = db_snapshot(conn)
    http_get("/api/v1/customers/DEMO-001", api_key)
    after = db_snapshot(conn)
    assert before == after


def test_no_write_on_404(conn, api_key):
    before = db_snapshot(conn)
    http_get("/api/v1/customers/DEMO-XXXX", api_key)
    after = db_snapshot(conn)
    assert before == after


def test_no_write_on_401(conn):
    before = db_snapshot(conn)
    http_get("/api/v1/customers/DEMO-001")
    after = db_snapshot(conn)
    assert before == after


def test_no_write_on_422(conn, api_key):
    before = db_snapshot(conn)
    http_get("/api/v1/customers/invalid!!", api_key)
    after = db_snapshot(conn)
    assert before == after


def test_error_body_no_internal_detail(api_key):
    responses = [
        http_get("/api/v1/customers/DEMO-XXXX", api_key),   # 404
        http_get("/api/v1/customers/DEMO-001"),              # 401
        http_get("/api/v1/customers/invalid!!"),             # 422
    ]
    for resp in responses:
        text = resp.text
        for forbidden in LEAK_STRINGS:
            assert forbidden not in text, (
                f"Response body leaks '{forbidden}': {text!r}"
            )


def test_503_on_db_down(api_key):
    client = docker.from_env()
    container = client.containers.get(POSTGRES_CONTAINER)
    try:
        container.stop(timeout=5)
        # Give the app a moment to notice the connection is gone
        time.sleep(2)
        resp = http_get("/api/v1/customers/DEMO-001", api_key)
        assert resp.status_code == 503
        assert resp.json() == {"error": "Service temporarily unavailable", "status": 503}
    finally:
        container.start()
        # Wait for postgres to be ready again before the test suite continues
        for _ in range(20):
            time.sleep(2)
            container.reload()
            if container.status == "running":
                health = container.attrs.get("State", {}).get("Health", {}).get("Status")
                if health == "healthy":
                    break
