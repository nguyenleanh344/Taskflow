from fastapi import FastAPI

from app.api.v1.auth import router as auth_router
from app.api.v1.projects import router as projects_router
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

app.include_router(
    auth_router,
    prefix="/api/v1",
)

app.include_router(
    projects_router,
    prefix="/api/v1",
)
