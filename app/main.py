from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.users import router as users_router
from app.core.database import engine
from app.models.user import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield


app = FastAPI(
    title="Backend Lab",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(
    users_router,
    prefix="/api/v1",
)