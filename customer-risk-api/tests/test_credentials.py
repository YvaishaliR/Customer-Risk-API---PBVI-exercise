import os

import httpx
import pytest

BASE_URL = "http://localhost:8000"


@pytest.fixture(scope="module")
def real_api_key():
    return os.environ["API_KEY"]


def full_response_text(resp: httpx.Response) -> str:
    header_str = " ".join(f"{k}: {v}" for k, v in resp.headers.items())
    return header_str + " " + resp.text


def get(path, api_key=None):
    headers = {"X-API-Key": api_key} if api_key else {}
    with httpx.Client(base_url=BASE_URL) as client:
        return client.get(path, headers=headers)


def test_key_not_in_200_response(real_api_key):
    resp = get("/api/v1/customers/DEMO-001", real_api_key)
    assert real_api_key not in full_response_text(resp)


def test_key_not_in_401_response(real_api_key):
    resp = get("/api/v1/customers/DEMO-001")
    assert real_api_key not in full_response_text(resp)


def test_key_not_in_404_response(real_api_key):
    resp = get("/api/v1/customers/DEMO-XXXX", real_api_key)
    assert real_api_key not in full_response_text(resp)


def test_key_not_in_422_response(real_api_key):
    resp = get("/api/v1/customers/invalid!!", real_api_key)
    assert real_api_key not in full_response_text(resp)


def test_key_not_in_html(real_api_key):
    resp = get("/")
    assert real_api_key not in resp.text


def test_key_not_in_response_headers(real_api_key):
    resp = get("/api/v1/customers/DEMO-001", real_api_key)
    for value in resp.headers.values():
        assert real_api_key not in value, f"API key found in header value: {value!r}"
