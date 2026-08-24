from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.services.user import UserService


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    data: UserCreate,
    session: AsyncSession = Depends(get_db),
):
    service = UserService(session)

    return await service.create_user(data)


@router.get(
    "/me",
    response_model=UserResponse,
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.get("/admin-only")
async def admin_only(
    current_user: User = Depends(require_role("admin")),
):
    return {
        "message": "You are an admin",
        "user_id": current_user.id,
    }
