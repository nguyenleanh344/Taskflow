from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.user import User
from app.repositories.project_repository import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectNotFoundError(Exception):
    pass


class ProjectForbiddenError(Exception):
    pass


class ProjectService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = ProjectRepository(session)

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

        await self.session.commit()
        await self.session.refresh(project)

        return project

    async def list_projects(self, current_user: User) -> list[Project]:
        if current_user.role == "admin":
            return await self.repository.list_all()

        return await self.repository.list_by_owner(current_user.id)

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
        project = await self._get_authorized_project(project_id, current_user)

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(project, field, value)

        await self.session.commit()
        await self.session.refresh(project)

        return project

    async def delete_project(
        self,
        project_id: int,
        current_user: User,
    ) -> None:
        project = await self._get_authorized_project(project_id, current_user)

        await self.repository.delete(project)
        await self.session.commit()

    async def _get_authorized_project(
        self,
        project_id: int,
        current_user: User,
    ) -> Project:
        project = await self.repository.get_by_id(project_id)

        if project is None:
            raise ProjectNotFoundError

        if project.owner_id != current_user.id and current_user.role != "admin":
            raise ProjectForbiddenError

        return project
