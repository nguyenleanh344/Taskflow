from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task


class TaskRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        title: str,
        description: str | None,
        status: str,
        project_id: int,
    ) -> Task:
        task = Task(
            title=title,
            description=description,
            status=status,
            project_id=project_id,
        )

        self.session.add(task)
        await self.session.flush()

        return task

    async def get_by_id(
        self,
        task_id: int,
    ) -> Task | None:
        result = await self.session.execute(
            select(Task).where(Task.id == task_id)
        )

        return result.scalar_one_or_none()

    async def list_by_project(
        self,
        project_id: int,
        status: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Task]:

        query = (
            select(Task)
            .where(Task.project_id == project_id)
            .order_by(Task.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        if status is not None:
            query = query.where(Task.status == status)

        result = await self.session.execute(query)

        return list(result.scalars().all())

    async def delete(self, task: Task) -> None:
        await self.session.delete(task)