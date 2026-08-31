from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.exceptions.handlers import register_exception_handlers
from app.api.v1.auth import router as auth_router
from app.api.v1.projects import router as projects_router
from app.api.v1.users import router as users_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.comments import router as comments_router
from app.api.v1.project_member import router as project_members_router
from app.cache.redis import close_redis


app = FastAPI(
    title="Backend Lab",
    version="0.1.0",
)

Instrumentator().instrument(app).expose(
    app,
    endpoint="/metrics",
    include_in_schema=False,
)

register_exception_handlers(app)


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

app.include_router(
    tasks_router,
    prefix="/api/v1",
)
app.include_router(
    comments_router,
    prefix="/api/v1",
)
app.include_router(
    project_members_router,
    prefix="/api/v1",
)


@app.on_event("shutdown")
async def shutdown_redis():
    await close_redis()
