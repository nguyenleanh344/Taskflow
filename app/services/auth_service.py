from datetime import datetime, timedelta, timezone

from app.core.unit_of_work import UnitOfWork
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_refresh_token,
    verify_password,
)
from app.core.config import settings
from app.models.user import User
from app.exceptions.auth import (
    InactiveUserError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
)
from app.schemas.auth import LoginRequest


class AuthService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.session = uow.session
        self.user_repository = uow.users
        self.refresh_repository = uow.refresh_tokens

    async def login(
        self,
        data: LoginRequest,
    ) -> tuple[str, str]:

        user = await self.user_repository.get_by_email(data.email)

        if user is None:
            raise InvalidCredentialsError

        if not verify_password(
            data.password,
            user.password_hash,
        ):
            raise InvalidCredentialsError

        if not user.is_active:
            raise InactiveUserError

        access_token = create_access_token(user.id)

        refresh_token = create_refresh_token()

        refresh_token_hash = hash_refresh_token(refresh_token)

        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.refresh_token_expire_days
        )

        await self.refresh_repository.create(
            token_hash=refresh_token_hash,
            user_id=user.id,
            expires_at=expires_at,
        )

        await self.uow.commit()

        return access_token, refresh_token

    async def refresh_access_token(
        self,
        refresh_token: str,
    ) -> tuple[str, str]:
        token_hash = hash_refresh_token(refresh_token)
        stored_token = await self.refresh_repository.get_by_hash(
            token_hash,
        )

        if stored_token is None:
            raise InvalidRefreshTokenError

        now = datetime.now(timezone.utc)
        expires_at = stored_token.expires_at

        # Some database drivers may return a naive datetime even when the
        # column is configured with timezone=True.
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if stored_token.revoked_at is not None or expires_at <= now:
            raise InvalidRefreshTokenError

        user = await self.session.get(User, stored_token.user_id)

        if user is None or not user.is_active:
            raise InvalidRefreshTokenError

        new_access_token = create_access_token(user.id)
        new_refresh_token = create_refresh_token()
        new_refresh_token_hash = hash_refresh_token(new_refresh_token)
        new_expires_at = now + timedelta(
            days=settings.refresh_token_expire_days,
        )

        await self.refresh_repository.revoke(stored_token)
        await self.refresh_repository.create(
            token_hash=new_refresh_token_hash,
            user_id=user.id,
            expires_at=new_expires_at,
        )

        await self.uow.commit()

        return new_access_token, new_refresh_token
