from collections.abc import AsyncIterator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.comment_repository import CommentRepository
from app.repositories.project_member_repository import ProjectMemberRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.refresh_token import RefreshTokenRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.user import UserRepository


class UnitOfWork:
    """Owns one database session and the repositories using that session."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.users = UserRepository(session)
        self.projects = ProjectRepository(session)
        self.tasks = TaskRepository(session)
        self.comments = CommentRepository(session)
        self.project_members = ProjectMemberRepository(session)
        self.refresh_tokens = RefreshTokenRepository(session)

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()

    async def __aenter__(self) -> "UnitOfWork":
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        if exc_type is not None:
            await self.rollback()


async def get_unit_of_work(
    session: AsyncSession = Depends(get_db),
) -> AsyncIterator[UnitOfWork]:
    uow = UnitOfWork(session)

    try:
        yield uow
    except Exception:
        await uow.rollback()
        raise
