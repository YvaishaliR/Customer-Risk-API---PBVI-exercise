import os

import httpx
import pytest

from app.db import get_conn, release_conn

BASE_URL = "http://localhost:8000"
ALL_IDS = [f"DEMO-{i:03d}" for i in range(1, 10)]


def ui_lookup(customer_id):
    with httpx.Client(base_url=BASE_URL) as client:
        return client.post("/ui/lookup", json={"customer_id": customer_id})


@pytest.fixture(scope="module")
def conn():
    c = get_conn()
    yield c
    try:
        release_conn(c)
    except Exception:
        pass


def db_fetch_all(conn):
    """Return {customer_id: {'risk_tier': str, 'risk_factors': list}} for all 9 records."""
    cur = conn.cursor()
    cur.execute(
        "SELECT customer_id, risk_tier::text, risk_factors FROM risk_profiles ORDER BY customer_id"
    )
    return {row[0]: {"risk_tier": row[1], "risk_factors": list(row[2]) if row[2] else []} for row in cur.fetchall()}


def test_ui_lookup_demo001_exact():
    resp = ui_lookup("DEMO-001")
    assert resp.status_code == 200
    assert resp.json() == {
        "customer_id": "DEMO-001",
        "risk_tier": "LOW",
        "risk_factors": [
            "Low transaction volume",
            "Account age > 5 years",
            "No adverse history",
        ],
    }


def test_ui_tier_verbatim_all_records(conn):
    db = db_fetch_all(conn)
    for customer_id in ALL_IDS:
        resp = ui_lookup(customer_id)
        assert resp.status_code == 200, f"{customer_id} returned {resp.status_code}"
        assert resp.json()["risk_tier"] == db[customer_id]["risk_tier"], (
            f"{customer_id}: UI tier {resp.json()['risk_tier']!r} != DB tier {db[customer_id]['risk_tier']!r}"
        )


def test_ui_factor_order_preserved(conn):
    resp = ui_lookup("DEMO-007")
    assert resp.status_code == 200
    cur = conn.cursor()
    cur.execute(
        "SELECT risk_factors FROM risk_profiles WHERE customer_id = 'DEMO-007'"
    )
    db_factors = list(cur.fetchone()[0])
    assert resp.json()["risk_factors"] == db_factors


def test_ui_factor_count_matches_db(conn):
    db = db_fetch_all(conn)
    for customer_id in ALL_IDS:
        resp = ui_lookup(customer_id)
        assert resp.status_code == 200
        ui_count = len(resp.json()["risk_factors"])
        db_count = len(db[customer_id]["risk_factors"])
        assert ui_count == db_count, (
            f"{customer_id}: UI factor count {ui_count} != DB count {db_count}"
        )


def test_ui_key_not_in_lookup_response():
    api_key = os.environ["API_KEY"]
    resp = ui_lookup("DEMO-001")
    assert api_key not in resp.text


def test_ui_error_envelope_shape():
    resp = ui_lookup("DEMO-XXXX")
    body = resp.json()
    assert "error" in body
    assert "status" in body
