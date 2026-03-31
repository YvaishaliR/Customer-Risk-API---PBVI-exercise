import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path

from app.auth import verify_api_key
from app.db import get_conn, release_conn

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/customers")


@router.get("/{customer_id}")
def get_customer(
    customer_id: Annotated[str, Path(max_length=20, pattern=r"^[A-Z0-9-]{1,20}$")],
    _key: str = Depends(verify_api_key),
):
    conn = get_conn()
    try:
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT customer_id, risk_tier, risk_factors FROM risk_profiles WHERE customer_id = %s",
                (customer_id,),
            )
            row = cur.fetchone()
        except Exception:
            logger.error("DB error on customer lookup")
            raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    finally:
        release_conn(conn)

    if row is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    return {
        "customer_id": row[0],
        "risk_tier": row[1],
        "risk_factors": list(row[2]) if row[2] else [],
    }
