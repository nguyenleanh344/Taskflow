from app.core.unit_of_work import UnitOfWork
from app.core.authorization.factory import get_project_authorization_strategy
from app.exceptions.resources import (
    MemberAlreadyExistsError,
    MemberNotFoundError,
    ProjectMemberForbiddenError,
    ProjectNotFoundError,
    UserNotFoundError,
)
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.user import User
from sqlalchemy.exc import IntegrityError


class ProjectMemberService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.session = uow.session
        self.repository = uow.project_members

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

        try:
            member = await self.repository.create(
                project_id=project.id,
                user_id=user.id,
            )

            await self.uow.commit()

        except IntegrityError as exc:
            await self.uow.rollback()

            constraint_name = getattr(
                exc.orig,
                "constraint_name",
                None,
            )

            if constraint_name == "uq_project_member":
                raise MemberAlreadyExistsError from exc

            raise

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

        await self.uow.commit()

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

        strategy = get_project_authorization_strategy(current_user)

        if not strategy.can_manage_members(project, current_user):
            raise ProjectMemberForbiddenError

        return project
