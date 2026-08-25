from app.core.authorization.factory import get_project_authorization_strategy
from app.core.pagination import PageResult
from app.core.unit_of_work import UnitOfWork
from app.exceptions.resources import ProjectForbiddenError, ProjectNotFoundError
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.repository = uow.projects

    async def create_project(
        self,
        data: ProjectCreate,
        current_user: User,
    ) -> Project:
        project = await self.repository.create(
            name=data.name,
            description=data.description,
            owner_id=current_user.id,
        )

        await self.uow.commit()
        await self.uow.session.refresh(project)

        return project

    async def list_projects(
        self,
        current_user: User,
        page: int = 1,
        limit: int = 20,
    ) -> PageResult[Project]:
        strategy = get_project_authorization_strategy(current_user)
        offset = (page - 1) * limit

        if strategy.can_list_all(current_user):
            items = await self.repository.list_all(offset=offset, limit=limit)
            total = await self.repository.count_all()
        else:
            items = await self.repository.list_by_owner(
                current_user.id,
                offset=offset,
                limit=limit,
            )
            total = await self.repository.count_by_owner(current_user.id)

        return PageResult(items=items, page=page, limit=limit, total=total)

    async def get_project(
        self,
        project_id: int,
        current_user: User,
    ) -> Project:
        project = await self._get_authorized_project(project_id, current_user)
        return project

    async def update_project(
        self,
        project_id: int,
        data: ProjectUpdate,
        current_user: User,
    ) -> Project:
        project = await self.repository.get_by_id(project_id)

        if project is None:
            raise ProjectNotFoundError

        strategy = get_project_authorization_strategy(current_user)

        if not strategy.can_update(
            project,
            current_user,
        ):
            raise ProjectForbiddenError

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(project, field, value)

        await self.uow.commit()
        await self.uow.session.refresh(project)

        return project

    async def delete_project(
        self,
        project_id: int,
        current_user: User,
    ) -> None:
        project = await self.repository.get_by_id(project_id)

        if project is None:
            raise ProjectNotFoundError

        strategy = get_project_authorization_strategy(current_user)

        if not strategy.can_delete(
            project,
            current_user,
        ):
            raise ProjectForbiddenError

        await self.repository.delete(project)

        await self.uow.commit()

    async def _get_authorized_project(
        self,
        project_id: int,
        current_user: User,
    ) -> Project:
        project = await self.repository.get_by_id(project_id)

        if project is None:
            raise ProjectNotFoundError

        strategy = get_project_authorization_strategy(current_user)

        if not strategy.can_access(
            project,
            current_user,
        ):
            raise ProjectForbiddenError

        return project
