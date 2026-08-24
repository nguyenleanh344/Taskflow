from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.project_member import ProjectMemberResponse
from app.services.project_member_service import (
    MemberAlreadyExistsError,
    MemberNotFoundError,
    ProjectMemberForbiddenError,
    ProjectMemberService,
    ProjectNotFoundError,
    UserNotFoundError,
)


router = APIRouter(
    prefix="/projects/{project_id}/members",
    tags=["project-members"],
)


def get_project_member_service(
    session: AsyncSession = Depends(get_db),
) -> ProjectMemberService:
    return ProjectMemberService(session)


def raise_member_http_error(error: Exception) -> None:

    if isinstance(
        error,
        (
            ProjectNotFoundError,
            UserNotFoundError,
            MemberNotFoundError,
        ),
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        )

    if isinstance(error, MemberAlreadyExistsError):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already a member of this project",
        )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to manage this project",
    )


@router.post(
    "/{user_id}",
    response_model=ProjectMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_member(
    project_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    service: ProjectMemberService = Depends(
        get_project_member_service,
    ),
):
    try:
        return await service.add_member(
            project_id,
            user_id,
            current_user,
        )

    except (
        ProjectNotFoundError,
        UserNotFoundError,
        MemberAlreadyExistsError,
        ProjectMemberForbiddenError,
    ) as exc:
        raise_member_http_error(exc)


@router.get(
    "",
    response_model=list[ProjectMemberResponse],
)
async def list_members(
    project_id: int,
    current_user: User = Depends(get_current_user),
    service: ProjectMemberService = Depends(
        get_project_member_service,
    ),
):
    try:
        return await service.list_members(
            project_id,
            current_user,
        )

    except (
        ProjectNotFoundError,
        ProjectMemberForbiddenError,
    ) as exc:
        raise_member_http_error(exc)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_member(
    project_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    service: ProjectMemberService = Depends(
        get_project_member_service,
    ),
):
    try:
        await service.remove_member(
            project_id,
            user_id,
            current_user,
        )

    except (
        ProjectNotFoundError,
        MemberNotFoundError,
        ProjectMemberForbiddenError,
    ) as exc:
        raise_member_http_error(exc)

    return None