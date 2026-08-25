from sqlalchemy.exc import IntegrityError

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

        try:
            user = await self.repository.create(
                email=data.email,
                password_hash=password_hash,
                name=data.name,
            )

            await self.uow.commit()

        except IntegrityError as exc:
            await self.uow.rollback()

            constraint_name = getattr(
                exc.orig,
                "constraint_name",
                None,
            )

            if constraint_name == "users_email_key":
                raise EmailAlreadyExistsError from exc

            raise

        await self.uow.session.refresh(user)

        return user
