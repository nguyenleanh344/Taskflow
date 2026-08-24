from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.project_service import (
    ProjectForbiddenError,
    ProjectNotFoundError,
    ProjectService,
)


router = APIRouter(
    prefix="/projects",
    tags=["projects"],
)


def get_project_service(session: AsyncSession = Depends(get_db)) -> ProjectService:
    return ProjectService(session)


def raise_project_http_error(error: Exception) -> None:
    if isinstance(error, ProjectNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to access this project",
    )


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_project(
    data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
):
    return await service.create_project(data, current_user)


@router.get(
    "",
    response_model=list[ProjectResponse],
)
async def list_projects(
    current_user: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
):
    return await service.list_projects(current_user)


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
):
    try:
        return await service.get_project(project_id, current_user)
    except (ProjectNotFoundError, ProjectForbiddenError) as exc:
        raise_project_http_error(exc)


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
)
async def update_project(
    project_id: int,
    data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
):
    try:
        return await service.update_project(project_id, data, current_user)
    except (ProjectNotFoundError, ProjectForbiddenError) as exc:
        raise_project_http_error(exc)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
):
    try:
        await service.delete_project(project_id, current_user)
    except (ProjectNotFoundError, ProjectForbiddenError) as exc:
        raise_project_http_error(exc)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
