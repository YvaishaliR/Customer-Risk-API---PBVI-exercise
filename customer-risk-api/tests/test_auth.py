import httpx

BASE_URL = "http://localhost:8000"
CUSTOMER_PATH = "/api/v1/customers/DEMO-001"


def test_no_key_returns_401():
    with httpx.Client(base_url=BASE_URL) as client:
        resp = client.get(CUSTOMER_PATH)
    assert resp.status_code == 401


def test_wrong_key_returns_401():
    with httpx.Client(base_url=BASE_URL) as client:
        resp = client.get(CUSTOMER_PATH, headers={"X-API-Key": "wrongkey"})
    assert resp.status_code == 401


def test_near_miss_key_returns_401(api_key):
    near_miss = api_key[:-1]
    with httpx.Client(base_url=BASE_URL) as client:
        resp = client.get(CUSTOMER_PATH, headers={"X-API-Key": near_miss})
    assert resp.status_code == 401


def test_401_body_shape():
    with httpx.Client(base_url=BASE_URL) as client:
        resp = client.get(CUSTOMER_PATH)
    assert resp.json() == {"error": "Unauthorized", "status": 401}


def test_docs_unauthenticated():
    with httpx.Client(base_url=BASE_URL) as client:
        resp = client.get("/docs")
    assert resp.status_code == 404


def test_openapi_unauthenticated():
    with httpx.Client(base_url=BASE_URL) as client:
        resp = client.get("/openapi.json")
    assert resp.status_code == 404
