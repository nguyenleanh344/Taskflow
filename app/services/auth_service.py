from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    verify_password,
)
from app.repositories.user import UserRepository
from app.schemas.auth import LoginRequest


class AuthService:

    def __init__(self, session: AsyncSession):
        self.repository = UserRepository(session)

    async def login(self, data: LoginRequest) -> str:

        user = await self.repository.get_by_email(
            data.email
        )

        if user is None:
            raise ValueError("Invalid credentials")

        if not verify_password(
            data.password,
            user.password_hash,
        ):
            raise ValueError("Invalid credentials")

        if not user.is_active:
            raise ValueError("User is inactive")

        return create_access_token(user.id)