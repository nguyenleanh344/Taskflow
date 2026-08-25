from fastapi import APIRouter, Depends, status
from app.core.dependencies import get_current_user
from app.core.unit_of_work import UnitOfWork, get_unit_of_work
from app.models.user import User
from app.schemas.project_member import ProjectMemberResponse
from app.services.project_member_service import ProjectMemberService


router = APIRouter(
    prefix="/projects/{project_id}/members",
    tags=["project-members"],
)


def get_project_member_service(
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> ProjectMemberService:
    return ProjectMemberService(uow)


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
    return await service.add_member(project_id, user_id, current_user)


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
    return await service.list_members(project_id, current_user)


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
    await service.remove_member(project_id, user_id, current_user)

    return None
