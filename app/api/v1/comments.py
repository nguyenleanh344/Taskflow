from fastapi import APIRouter, Body, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.comment import (
    CommentCreate,
    CommentResponse,
    CommentUpdate,
)
from app.services.comment_service import (
    CommentForbiddenError,
    CommentNotFoundError,
    CommentService,
    TaskNotFoundError,
)


router = APIRouter(
    prefix="/projects/{project_id}/tasks/{task_id}/comments",
    tags=["comments"],
)


def get_comment_service(
    session: AsyncSession = Depends(get_db),
) -> CommentService:
    return CommentService(session)


def raise_comment_http_error(error: Exception) -> None:
    if isinstance(
        error,
        (CommentNotFoundError, TaskNotFoundError),
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to access this resource",
    )


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
    try:
        return await service.create_comment(
            project_id,
            task_id,
            data,
            current_user,
        )

    except (
        CommentForbiddenError,
        TaskNotFoundError,
    ) as exc:
        raise_comment_http_error(exc)


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
    try:
        return await service.list_comments(
            project_id,
            task_id,
            current_user,
        )

    except (
        CommentForbiddenError,
        TaskNotFoundError,
    ) as exc:
        raise_comment_http_error(exc)


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
    try:
        return await service.get_comment(
            project_id,
            task_id,
            comment_id,
            current_user,
        )

    except (
        CommentNotFoundError,
        CommentForbiddenError,
        TaskNotFoundError,
    ) as exc:
        raise_comment_http_error(exc)


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
    try:
        return await service.update_comment(
            project_id,
            task_id,
            comment_id,
            data,
            current_user,
        )

    except (
        CommentNotFoundError,
        CommentForbiddenError,
        TaskNotFoundError,
    ) as exc:
        raise_comment_http_error(exc)


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
    try:
        await service.delete_comment(
            project_id,
            task_id,
            comment_id,
            current_user,
        )

    except (
        CommentNotFoundError,
        CommentForbiddenError,
        TaskNotFoundError,
    ) as exc:
        raise_comment_http_error(exc)

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )
