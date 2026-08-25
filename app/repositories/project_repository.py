from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project


class ProjectRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        name: str,
        description: str | None,
        owner_id: int,
    ) -> Project:
        project = Project(
            name=name,
            description=description,
            owner_id=owner_id,
        )

        self.session.add(project)
        await self.session.flush()

        return project

    async def get_by_id(self, project_id: int) -> Project | None:
        result = await self.session.execute(
            select(Project).where(Project.id == project_id)
        )

        return result.scalar_one_or_none()

    async def list_all(self, offset: int = 0, limit: int = 20) -> list[Project]:
        result = await self.session.execute(
            select(Project).order_by(Project.id).offset(offset).limit(limit)
        )

        return list(result.scalars().all())

    async def list_by_owner(
        self,
        owner_id: int,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Project]:
        result = await self.session.execute(
            select(Project)
            .where(Project.owner_id == owner_id)
            .order_by(Project.id)
            .offset(offset)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def count_all(self) -> int:
        result = await self.session.execute(select(func.count()).select_from(Project))
        return result.scalar_one()

    async def count_by_owner(self, owner_id: int) -> int:
        result = await self.session.execute(
            select(func.count())
            .select_from(Project)
            .where(Project.owner_id == owner_id)
        )
        return result.scalar_one()

    async def delete(self, project: Project) -> None:
        await self.session.delete(project)
