import httpx
import pytest

BASE_URL = "http://localhost:8000"
ALL_IDS = [f"DEMO-{i:03d}" for i in range(1, 10)]


def get(path, api_key, **kwargs):
    with httpx.Client(base_url=BASE_URL) as client:
        return client.get(path, headers={"X-API-Key": api_key}, **kwargs)


def test_demo001_exact(api_key):
    resp = get("/api/v1/customers/DEMO-001", api_key)
    assert resp.status_code == 200
    body = resp.json()
    assert body["customer_id"] == "DEMO-001"
    assert body["risk_tier"] == "LOW"
    assert body["risk_factors"] == [
        "Low transaction volume",
        "Account age > 5 years",
        "No adverse history",
    ]


def test_all_tiers_represented(api_key):
    cases = [("DEMO-001", "LOW"), ("DEMO-004", "MEDIUM"), ("DEMO-007", "HIGH")]
    for customer_id, expected_tier in cases:
        resp = get(f"/api/v1/customers/{customer_id}", api_key)
        assert resp.status_code == 200, f"{customer_id} returned {resp.status_code}"
        assert resp.json()["risk_tier"] == expected_tier, f"{customer_id} tier mismatch"


def test_response_has_exactly_three_fields(api_key):
    resp = get("/api/v1/customers/DEMO-001", api_key)
    assert resp.status_code == 200
    assert set(resp.json().keys()) == {"customer_id", "risk_tier", "risk_factors"}


def test_risk_tier_is_uppercase_enum(api_key):
    valid_tiers = {"LOW", "MEDIUM", "HIGH"}
    for customer_id in ALL_IDS:
        resp = get(f"/api/v1/customers/{customer_id}", api_key)
        assert resp.status_code == 200
        tier = resp.json()["risk_tier"]
        assert tier in valid_tiers, f"{customer_id} has unexpected tier: {repr(tier)}"
        assert tier == tier.strip(), f"{customer_id} tier has whitespace"


def test_risk_factors_is_list_never_null(api_key):
    for customer_id in ALL_IDS:
        resp = get(f"/api/v1/customers/{customer_id}", api_key)
        assert resp.status_code == 200
        assert isinstance(resp.json()["risk_factors"], list), f"{customer_id} risk_factors is not a list"


def test_unknown_id_returns_404(api_key):
    resp = get("/api/v1/customers/DEMO-XXXX", api_key)
    assert resp.status_code == 404


def test_404_body_shape(api_key):
    resp = get("/api/v1/customers/DEMO-XXXX", api_key)
    assert resp.json() == {"error": "Customer not found", "status": 404}
