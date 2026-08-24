from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project_member import ProjectMember


class ProjectMemberRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        project_id: int,
        user_id: int,
    ) -> ProjectMember:

        member = ProjectMember(
            project_id=project_id,
            user_id=user_id,
        )

        self.session.add(member)
        await self.session.flush()

        return member

    async def get(
        self,
        project_id: int,
        user_id: int,
    ) -> ProjectMember | None:

        result = await self.session.execute(
            select(ProjectMember).where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id,
            )
        )

        return result.scalar_one_or_none()

    async def list_by_project(
        self,
        project_id: int,
    ) -> list[ProjectMember]:

        result = await self.session.execute(
            select(ProjectMember)
            .where(ProjectMember.project_id == project_id)
            .order_by(ProjectMember.joined_at)
        )

        return list(result.scalars().all())

    async def delete(
        self,
        member: ProjectMember,
    ) -> None:

        await self.session.delete(member)
