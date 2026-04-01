import logging
import sys
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.db import get_conn, release_conn
from app.routers import customers, ui

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    for attempt in range(1, 11):
        try:
            conn = get_conn()
            release_conn(conn)
            logger.info("Database connection verified")
            break
        except Exception:
            if attempt < 10:
                time.sleep(2)
    else:
        logger.error("Database unreachable at startup")
        sys.exit(1)
    yield


app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)

app.include_router(customers.router)
app.include_router(ui.router)


@app.get("/healthz")
def healthz():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        release_conn(conn)
        return {"status": "ok"}
    except Exception:
        return JSONResponse(status_code=503, content={"status": "degraded"})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"error": "Invalid request", "status": 422})


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail, "status": exc.status_code})


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled error")
    return JSONResponse(status_code=500, content={"error": "Internal server error", "status": 500})


app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
