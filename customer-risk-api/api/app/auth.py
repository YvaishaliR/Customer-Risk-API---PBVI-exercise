import os

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(key: str = Security(api_key_header)) -> str:
    expected = os.environ["API_KEY"]
    if key is None or key != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return key
