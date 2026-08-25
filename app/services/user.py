from app.core.security import hash_password
from app.core.unit_of_work import UnitOfWork
from app.exceptions.resources import EmailAlreadyExistsError
from app.schemas.user import UserCreate


class UserService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.repository = uow.users

    async def create_user(self, data: UserCreate):

        existing_user = await self.repository.get_by_email(data.email)

        if existing_user:
            raise EmailAlreadyExistsError

        password_hash = hash_password(data.password)

        user = await self.repository.create(
            email=data.email,
            password_hash=password_hash,
            name=data.name,
        )

        await self.uow.commit()

        await self.uow.session.refresh(user)

        return user
