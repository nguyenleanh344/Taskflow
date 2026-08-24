from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.user import User
from app.repositories.project_member_repository import (
    ProjectMemberRepository,
)


class ProjectNotFoundError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class MemberAlreadyExistsError(Exception):
    pass


class MemberNotFoundError(Exception):
    pass


class ProjectMemberForbiddenError(Exception):
    pass


class ProjectMemberService:

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = ProjectMemberRepository(session)

    async def add_member(
        self,
        project_id: int,
        user_id: int,
        current_user: User,
    ) -> ProjectMember:

        project = await self._get_project(
            project_id,
            current_user,
        )

        user = await self.session.get(
            User,
            user_id,
        )

        if user is None:
            raise UserNotFoundError

        existing = await self.repository.get(
            project.id,
            user.id,
        )

        if existing is not None:
            raise MemberAlreadyExistsError

        member = await self.repository.create(
            project_id=project.id,
            user_id=user.id,
        )

        await self.session.commit()
        await self.session.refresh(member)

        return member

    async def list_members(
        self,
        project_id: int,
        current_user: User,
    ) -> list[ProjectMember]:

        await self._get_project(
            project_id,
            current_user,
        )

        return await self.repository.list_by_project(
            project_id,
        )

    async def remove_member(
        self,
        project_id: int,
        user_id: int,
        current_user: User,
    ) -> None:

        await self._get_project(
            project_id,
            current_user,
        )

        member = await self.repository.get(
            project_id,
            user_id,
        )

        if member is None:
            raise MemberNotFoundError

        await self.repository.delete(member)

        await self.session.commit()

    async def _get_project(
        self,
        project_id: int,
        current_user: User,
    ) -> Project:

        project = await self.session.get(
            Project,
            project_id,
        )

        if project is None:
            raise ProjectNotFoundError

        if (
            project.owner_id != current_user.id
            and current_user.role != "admin"
        ):
            raise ProjectMemberForbiddenError

        return project