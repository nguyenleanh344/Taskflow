from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment
from app.models.project import Project
from app.models.task import Task
from app.models.user import User
from app.repositories.comment_repository import CommentRepository
from app.schemas.comment import CommentCreate, CommentUpdate


class CommentNotFoundError(Exception):
    pass


class CommentForbiddenError(Exception):
    pass


class TaskNotFoundError(Exception):
    pass


class CommentService:

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = CommentRepository(session)

    async def create_comment(
        self,
        project_id: int,
        task_id: int,
        data: CommentCreate,
        current_user: User,
    ) -> Comment:

        await self._authorize_task(
            project_id,
            task_id,
            current_user,
        )

        comment = await self.repository.create(
            content=data.content,
            task_id=task_id,
            author_id=current_user.id,
        )

        await self.session.commit()
        await self.session.refresh(comment)

        return comment

    async def list_comments(
        self,
        project_id: int,
        task_id: int,
        current_user: User,
    ) -> list[Comment]:

        await self._authorize_task(
            project_id,
            task_id,
            current_user,
        )

        return await self.repository.list_by_task(task_id)

    async def get_comment(
        self,
        project_id: int,
        task_id: int,
        comment_id: int,
        current_user: User,
    ) -> Comment:

        await self._authorize_task(
            project_id,
            task_id,
            current_user,
        )

        comment = await self.repository.get_by_id(comment_id)

        if comment is None:
            raise CommentNotFoundError

        if comment.task_id != task_id:
            raise CommentNotFoundError

        return comment

    async def update_comment(
        self,
        project_id: int,
        task_id: int,
        comment_id: int,
        data: CommentUpdate,
        current_user: User,
    ) -> Comment:

        await self._authorize_task(
            project_id,
            task_id,
            current_user,
        )

        comment = await self.repository.get_by_id(comment_id)

        if comment is None:
            raise CommentNotFoundError

        if comment.task_id != task_id:
            raise CommentNotFoundError

        if (
            comment.author_id != current_user.id
            and current_user.role != "admin"
        ):
            raise CommentForbiddenError

        comment.content = data.content

        await self.session.commit()
        await self.session.refresh(comment)

        return comment

    async def delete_comment(
        self,
        project_id: int,
        task_id: int,
        comment_id: int,
        current_user: User,
    ) -> None:

        await self._authorize_task(
            project_id,
            task_id,
            current_user,
        )

        comment = await self.repository.get_by_id(comment_id)

        if comment is None:
            raise CommentNotFoundError

        if comment.task_id != task_id:
            raise CommentNotFoundError

        if (
            comment.author_id != current_user.id
            and current_user.role != "admin"
        ):
            raise CommentForbiddenError

        await self.repository.delete(comment)

        await self.session.commit()

    async def _authorize_task(
        self,
        project_id: int,
        task_id: int,
        current_user: User,
    ) -> Task:

        result = await self.session.execute(
            select(Task)
            .join(Project, Task.project_id == Project.id)
            .where(
                Task.id == task_id,
                Task.project_id == project_id,
            )
        )

        task = result.scalar_one_or_none()

        if task is None:
            raise TaskNotFoundError

        project = await self.session.get(
            Project,
            project_id,
        )

        if project is None:
            raise TaskNotFoundError

        if (
            project.owner_id != current_user.id
            and current_user.role != "admin"
        ):
            raise CommentForbiddenError

        return task