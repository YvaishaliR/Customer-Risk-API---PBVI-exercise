import os

import pytest

from app.db import get_conn, release_conn

EXPECTED_IDS = [f"DEMO-{i:03d}" for i in range(1, 10)]


@pytest.fixture(scope="module")
def conn():
    c = get_conn()
    yield c
    release_conn(c)


def test_row_count(conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM risk_profiles;")
    (count,) = cur.fetchone()
    assert count == 9


def test_all_ids_present(conn):
    cur = conn.cursor()
    cur.execute("SELECT customer_id FROM risk_profiles ORDER BY customer_id;")
    ids = [row[0] for row in cur.fetchall()]
    assert ids == EXPECTED_IDS


def test_tier_distribution(conn):
    cur = conn.cursor()
    cur.execute(
        "SELECT risk_tier::text, COUNT(*) FROM risk_profiles GROUP BY risk_tier ORDER BY risk_tier;"
    )
    distribution = {tier: count for tier, count in cur.fetchall()}
    assert distribution == {"HIGH": 3, "LOW": 3, "MEDIUM": 3}


def test_demo001_factors_exact(conn):
    cur = conn.cursor()
    cur.execute(
        "SELECT risk_factors FROM risk_profiles WHERE customer_id = 'DEMO-001';"
    )
    (factors,) = cur.fetchone()
    assert factors == [
        "Low transaction volume",
        "Account age > 5 years",
        "No adverse history",
    ]


def test_demo007_tier(conn):
    cur = conn.cursor()
    cur.execute(
        "SELECT risk_tier::text FROM risk_profiles WHERE customer_id = 'DEMO-007';"
    )
    (tier,) = cur.fetchone()
    assert tier == "HIGH"


def test_idempotency(conn):
    seed_path = os.path.join(os.path.dirname(__file__), "..", "db", "seed", "seed.sql")
    with open(seed_path) as f:
        sql = f.read()
    cur = conn.cursor()
    cur.execute(sql)
    conn.rollback()  # don't commit; just verify no error was raised

    cur.execute("SELECT COUNT(*) FROM risk_profiles;")
    (count,) = cur.fetchone()
    assert count == 9
