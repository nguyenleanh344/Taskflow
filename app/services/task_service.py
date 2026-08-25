from app.core.unit_of_work import UnitOfWork
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
        offset: int = 0,
        limit: int = 20,
    ) -> list[Task]:

        project = await self._get_authorized_project(
            project_id,
            current_user,
        )

        return await self.repository.list_by_project(
            project_id=project.id,
            status=status,
            offset=offset,
            limit=limit,
        )

    async def get_task(
        self,
        task_id: int,
        current_user: User,
    ) -> Task:

        task = await self.repository.get_by_id(task_id)

        if task is None:
            raise TaskNotFoundError

        await self._get_authorized_project(
            task.project_id,
            current_user,
        )

        return task

    async def update_task(
        self,
        task_id: int,
        data: TaskUpdate,
        current_user: User,
    ) -> Task:

        task = await self.repository.get_by_id(task_id)

        if task is None:
            raise TaskNotFoundError

        await self._get_authorized_project(
            task.project_id,
            current_user,
        )

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(task, field, value)

        await self.uow.commit()
        await self.uow.session.refresh(task)

        return task

    async def delete_task(
        self,
        task_id: int,
        current_user: User,
    ) -> None:

        task = await self.repository.get_by_id(task_id)

        if task is None:
            raise TaskNotFoundError

        await self._get_authorized_project(
            task.project_id,
            current_user,
        )

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

        if project.owner_id != current_user.id and current_user.role != "admin":
            raise TaskForbiddenError

        return project
