from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        token_hash: str,
        user_id: int,
        expires_at: datetime,
    ) -> RefreshToken:

        token = RefreshToken(
            token_hash=token_hash,
            user_id=user_id,
            expires_at=expires_at,
        )

        self.session.add(token)
        await self.session.flush()

        return token

    async def get_by_hash(
        self,
        token_hash: str,
    ) -> RefreshToken | None:

        result = await self.session.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )

        return result.scalar_one_or_none()

    async def revoke(
        self,
        token: RefreshToken,
    ) -> None:

        token.revoked_at = datetime.now(timezone.utc)
