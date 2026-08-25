from fastapi import APIRouter, Depends, Query, Response, status
from app.core.dependencies import get_current_user
from app.core.unit_of_work import UnitOfWork, get_unit_of_work
from app.models.user import User
from app.schemas.pagination import PageResponse
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.project_service import ProjectService


router = APIRouter(
    prefix="/projects",
    tags=["projects"],
)


def get_project_service(uow: UnitOfWork = Depends(get_unit_of_work)) -> ProjectService:
    return ProjectService(uow)


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
    response_model=PageResponse[ProjectResponse],
)
async def list_projects(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
):
    result = await service.list_projects(current_user, page=page, limit=limit)
    return PageResponse(
        items=result.items,
        page=result.page,
        limit=result.limit,
        total=result.total,
        has_next=result.has_next,
    )


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
):
    return await service.get_project(project_id, current_user)


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
    return await service.update_project(project_id, data, current_user)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
):
    await service.delete_project(project_id, current_user)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
