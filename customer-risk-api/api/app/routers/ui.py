import logging
import re

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.db import get_conn, release_conn
from app.routers.customers import CUSTOMER_ID_PATTERN, fetch_customer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ui")

_id_re = re.compile(CUSTOMER_ID_PATTERN)


class LookupRequest(BaseModel):
    customer_id: str


@router.post("/lookup")
def ui_lookup(body: LookupRequest):
    if not _id_re.match(body.customer_id):
        return JSONResponse(status_code=422, content={"error": "Invalid request", "status": 422})

    conn = get_conn()
    try:
        try:
            result = fetch_customer(body.customer_id, conn)
        except Exception:
            logger.error("DB error on customer lookup")
            return JSONResponse(
                status_code=503,
                content={"error": "Service temporarily unavailable", "status": 503},
            )
    finally:
        release_conn(conn)

    if result is None:
        return JSONResponse(status_code=404, content={"error": "Customer not found", "status": 404})

    return result
