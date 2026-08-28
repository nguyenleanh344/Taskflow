from typing import Literal

from sqlalchemy import func, select
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
        project_id: int | None = None,
    ) -> Task | None:
        query = select(Task).where(Task.id == task_id)

        if project_id is not None:
            query = query.where(Task.project_id == project_id)

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def list_by_project(
        self,
        project_id: int,
        status: str | None = None,
        offset: int = 0,
        limit: int = 20,
        sort_by: Literal["created_at", "updated_at", "title", "status"] = "created_at",
        order: Literal["asc", "desc"] = "desc",
    ) -> list[Task]:
        sort_columns = {
            "created_at": Task.created_at,
            "updated_at": Task.updated_at,
            "title": Task.title,
            "status": Task.status,
        }
        sort_column = sort_columns[sort_by]
        ordering = sort_column.asc() if order == "asc" else sort_column.desc()
        query = (
            select(Task)
            .where(Task.project_id == project_id)
            .order_by(ordering, Task.id)
            .offset(offset)
            .limit(limit)
        )

        if status is not None:
            query = query.where(Task.status == status)

        result = await self.session.execute(query)

        return list(result.scalars().all())

    async def count_by_project(
        self,
        project_id: int,
        status: str | None = None,
    ) -> int:
        query = (
            select(func.count()).select_from(Task).where(Task.project_id == project_id)
        )

        if status is not None:
            query = query.where(Task.status == status)

        result = await self.session.execute(query)
        return result.scalar_one()

    async def delete(self, task: Task) -> None:
        await self.session.delete(task)
