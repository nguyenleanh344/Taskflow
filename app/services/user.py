from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user import UserRepository
from app.schemas.user import UserCreate


class UserService:

    def __init__(self, session: AsyncSession):
        self.repository = UserRepository(session)
        self.session = session

    async def create_user(self, data: UserCreate):

        existing_user = await self.repository.get_by_email(
            data.email
        )

        if existing_user:
            raise ValueError("Email already exists")

        # Tạm thời chưa hash password.
        # Authentication sẽ làm ở phase sau.
        password_hash = data.password

        user = await self.repository.create(
            email=data.email,
            password_hash=password_hash,
            name=data.name,
        )

        await self.session.commit()

        await self.session.refresh(user)

        return user