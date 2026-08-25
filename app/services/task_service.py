from typing import Literal

from app.core.pagination import PageResult
from app.core.unit_of_work import UnitOfWork
from app.core.authorization.factory import get_project_authorization_strategy
from app.exceptions.resources import (
    ProjectNotFoundError,
    TaskForbiddenError,
    TaskNotFoundError,
)
from app.models.project import Project
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.repository = uow.tasks
        self.project_repository = uow.projects

    async def create_task(
        self,
        project_id: int,
        data: TaskCreate,
        current_user: User,
    ) -> Task:

        project = await self._get_authorized_project(
            project_id,
            current_user,
        )

        task = await self.repository.create(
            title=data.title,
            description=data.description,
            status=data.status,
            project_id=project.id,
        )

        await self.uow.commit()
        await self.uow.session.refresh(task)

        return task

    async def list_tasks(
        self,
        project_id: int,
        current_user: User,
        status: str | None = None,
        page: int = 1,
        limit: int = 20,
        sort_by: Literal["created_at", "updated_at", "title", "status"] = "created_at",
        order: Literal["asc", "desc"] = "desc",
    ) -> PageResult[Task]:

        project = await self._get_authorized_project(
            project_id,
            current_user,
        )

        offset = (page - 1) * limit
        items = await self.repository.list_by_project(
            project_id=project.id,
            status=status,
            offset=offset,
            limit=limit,
            sort_by=sort_by,
            order=order,
        )
        total = await self.repository.count_by_project(project.id, status=status)
        return PageResult(items=items, page=page, limit=limit, total=total)

    async def get_task(
        self,
        project_id: int,
        task_id: int,
        current_user: User,
    ) -> Task:
        await self._get_authorized_project(project_id, current_user)

        task = await self.repository.get_by_id(task_id)

        if task is None or task.project_id != project_id:
            raise TaskNotFoundError

        return task

    async def update_task(
        self,
        project_id: int,
        task_id: int,
        data: TaskUpdate,
        current_user: User,
    ) -> Task:
        await self._get_authorized_project(project_id, current_user)

        task = await self.repository.get_by_id(task_id)

        if task is None or task.project_id != project_id:
            raise TaskNotFoundError

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(task, field, value)

        await self.uow.commit()
        await self.uow.session.refresh(task)

        return task

    async def delete_task(
        self,
        project_id: int,
        task_id: int,
        current_user: User,
    ) -> None:
        await self._get_authorized_project(project_id, current_user)

        task = await self.repository.get_by_id(task_id)

        if task is None or task.project_id != project_id:
            raise TaskNotFoundError

        await self.repository.delete(task)

        await self.uow.commit()

    async def _get_authorized_project(
        self,
        project_id: int,
        current_user: User,
    ) -> Project:

        project = await self.project_repository.get_by_id(project_id)

        if project is None:
            raise ProjectNotFoundError

        strategy = get_project_authorization_strategy(current_user)

        if not strategy.can_access(project, current_user):
            raise TaskForbiddenError

        return project
