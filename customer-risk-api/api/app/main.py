from fastapi import FastAPI

from app.routers import customers

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

app.include_router(customers.router)


@app.get("/")
def root():
    return {"status": "ok"}
