from fastapi import APIRouter, Body, Depends, Response, status
from app.core.dependencies import get_current_user
from app.core.unit_of_work import UnitOfWork, get_unit_of_work
from app.models.user import User
from app.schemas.comment import (
    CommentCreate,
    CommentResponse,
    CommentUpdate,
)
from app.services.comment_service import CommentService


router = APIRouter(
    prefix="/projects/{project_id}/tasks/{task_id}/comments",
    tags=["comments"],
)


def get_comment_service(
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> CommentService:
    return CommentService(uow)


@router.post(
    "",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    project_id: int,
    task_id: int,
    data: CommentCreate = Body(...),
    current_user: User = Depends(get_current_user),
    service: CommentService = Depends(get_comment_service),
):
    return await service.create_comment(
        project_id,
        task_id,
        data,
        current_user,
    )


@router.get(
    "",
    response_model=list[CommentResponse],
)
async def list_comments(
    project_id: int,
    task_id: int,
    current_user: User = Depends(get_current_user),
    service: CommentService = Depends(get_comment_service),
):
    return await service.list_comments(
        project_id,
        task_id,
        current_user,
    )


@router.get(
    "/{comment_id}",
    response_model=CommentResponse,
)
async def get_comment(
    project_id: int,
    task_id: int,
    comment_id: int,
    current_user: User = Depends(get_current_user),
    service: CommentService = Depends(get_comment_service),
):
    return await service.get_comment(
        project_id,
        task_id,
        comment_id,
        current_user,
    )


@router.patch(
    "/{comment_id}",
    response_model=CommentResponse,
)
async def update_comment(
    project_id: int,
    task_id: int,
    comment_id: int,
    data: CommentUpdate = Body(...),
    current_user: User = Depends(get_current_user),
    service: CommentService = Depends(get_comment_service),
):
    return await service.update_comment(
        project_id,
        task_id,
        comment_id,
        data,
        current_user,
    )


@router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_comment(
    project_id: int,
    task_id: int,
    comment_id: int,
    current_user: User = Depends(get_current_user),
    service: CommentService = Depends(get_comment_service),
):
    await service.delete_comment(
        project_id,
        task_id,
        comment_id,
        current_user,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )
