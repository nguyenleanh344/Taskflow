from contextlib import asynccontextmanager

from fastapi import FastAPI

from fastapi import FastAPI

from app.api.v1.users import router as users_router


app = FastAPI(
    title="Backend Lab",
    version="0.1.0",
)


@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(
    users_router,
    prefix="/api/v1",
)