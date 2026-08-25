from typing import Literal

from fastapi import APIRouter, Depends, Query, Response, status
from app.core.dependencies import get_current_user
from app.core.unit_of_work import UnitOfWork, get_unit_of_work
from app.models.user import User
from app.schemas.pagination import PageResponse
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.services.task_service import TaskService


router = APIRouter(
    prefix="/projects/{project_id}/tasks",
    tags=["tasks"],
)


def get_task_service(
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> TaskService:
    return TaskService(uow)


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    project_id: int,
    data: TaskCreate,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    return await service.create_task(
        project_id,
        data,
        current_user,
    )


@router.get(
    "",
    response_model=PageResponse[TaskResponse],
)
async def list_tasks(
    project_id: int,
    status_filter: str | None = Query(
        default=None,
        alias="status",
    ),
    page: int = Query(default=1, ge=1),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    sort_by: Literal["created_at", "updated_at", "title", "status"] = Query(
        default="created_at"
    ),
    order: Literal["asc", "desc"] = Query(default="desc"),
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    result = await service.list_tasks(
        project_id=project_id,
        current_user=current_user,
        status=status_filter,
        page=page,
        limit=limit,
        sort_by=sort_by,
        order=order,
    )
    return PageResponse(
        items=result.items,
        page=result.page,
        limit=result.limit,
        total=result.total,
        has_next=result.has_next,
    )


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
)
async def get_task(
    project_id: int,
    task_id: int,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    return await service.get_task(project_id, task_id, current_user)


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
)
async def update_task(
    project_id: int,
    task_id: int,
    data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    return await service.update_task(project_id, task_id, data, current_user)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_task(
    project_id: int,
    task_id: int,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    await service.delete_task(project_id, task_id, current_user)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
