import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path

from app.auth import verify_api_key
from app.db import get_conn, release_conn

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/customers")

CUSTOMER_ID_PATTERN = r"^[A-Z0-9-]{1,20}$"


def fetch_customer(customer_id: str, conn):
    """Execute the customer lookup query and return a dict or None."""
    cur = conn.cursor()
    cur.execute(
        "SELECT customer_id, risk_tier, risk_factors FROM risk_profiles WHERE customer_id = %s",
        (customer_id,),
    )
    row = cur.fetchone()
    if row is None:
        return None
    return {
        "customer_id": row[0],
        "risk_tier": row[1],
        "risk_factors": list(row[2]) if row[2] else [],
    }


@router.get("/{customer_id}")
def get_customer(
    customer_id: Annotated[str, Path(max_length=20, pattern=CUSTOMER_ID_PATTERN)],
    _key: str = Depends(verify_api_key),
):
    conn = get_conn()
    try:
        try:
            result = fetch_customer(customer_id, conn)
        except Exception:
            logger.error("DB error on customer lookup")
            raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    finally:
        release_conn(conn)

    if result is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    return result
