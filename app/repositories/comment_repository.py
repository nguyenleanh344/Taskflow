from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment


class CommentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        content: str,
        task_id: int,
        author_id: int,
    ) -> Comment:
        comment = Comment(
            content=content,
            task_id=task_id,
            author_id=author_id,
        )

        self.session.add(comment)
        await self.session.flush()

        return comment

    async def get_by_id(
        self,
        comment_id: int,
    ) -> Comment | None:
        result = await self.session.execute(
            select(Comment).where(Comment.id == comment_id)
        )

        return result.scalar_one_or_none()

    async def list_by_task(
        self,
        task_id: int,
    ) -> list[Comment]:
        result = await self.session.execute(
            select(Comment)
            .where(Comment.task_id == task_id)
            .order_by(Comment.created_at)
        )

        return list(result.scalars().all())

    async def delete(
        self,
        comment: Comment,
    ) -> None:
        await self.session.delete(comment)
