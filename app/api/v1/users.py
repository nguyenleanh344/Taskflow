from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services.user import UserService
from app.models.user import User

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

@router.post("/test-rollback")
async def test_rollback(
    session: AsyncSession = Depends(get_db),
):
    user = User(
        email="rollback@example.com",
        password_hash="test",
        name="Rollback User",
    )

    session.add(user)

    await session.flush()

    print(f"User ID after flush: {user.id}")

    raise RuntimeError("Something went wrong!")

    await session.commit()

    return {"id": user.id}