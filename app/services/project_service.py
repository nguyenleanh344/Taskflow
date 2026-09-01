from app.core.authorization.factory import get_project_authorization_strategy
from app.core.pagination import PageResult
from app.core.unit_of_work import UnitOfWork
from app.exceptions.resources import ProjectForbiddenError, ProjectNotFoundError
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate
from datetime import datetime

from redis.exceptions import RedisError

from app.cache.keys import project_key
from app.cache.redis import RedisCache
from app.core.config import settings


class ProjectService:
    def __init__(
        self,
        uow: UnitOfWork,
        cache: RedisCache | None = None,
        event_publisher=None,
    ):
        self.uow = uow
        self.repository = uow.projects
        self.cache = cache
        self.event_publisher = event_publisher

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

        if self.event_publisher is not None:
            await self.event_publisher.publish(
                routing_key="project.created",
                payload={
                    "project_id": project.id,
                    "name": project.name,
                    "owner_id": project.owner_id,
                },
            )

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

    async def _invalidate_project_cache(
        self,
        project_id: int,
    ) -> None:
        if self.cache is None:
            return

        await self.cache.delete(project_key(project_id))

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

        await self._invalidate_project_cache(project_id)

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

        await self._invalidate_project_cache(project_id)

    async def _get_authorized_project(
        self,
        project_id: int,
        current_user: User,
    ) -> Project:
        project = None

        # 1. Try cache
        if self.cache is not None:
            try:
                cached = await self.cache.get_json(project_key(project_id))
            except RedisError:
                cached = None

            if cached is not None:
                project = Project(
                    id=cached["id"],
                    name=cached["name"],
                    description=cached.get("description"),
                    owner_id=cached["owner_id"],
                    created_at=datetime.fromisoformat(cached["created_at"]),
                )

        # 2. Cache miss → database
        if project is None:
            project = await self.repository.get_by_id(project_id)

            if project is None:
                raise ProjectNotFoundError

            # 3. Store in cache
            await self._cache_project(project)

        # 4. Authorization vẫn phải được thực hiện
        strategy = get_project_authorization_strategy(current_user)

        if not strategy.can_access(
            project,
            current_user,
        ):
            raise ProjectForbiddenError

        return project

    async def _cache_project(
        self,
        project: Project,
    ) -> None:
        if self.cache is None:
            return

        await self.cache.set_json(
            project_key(project.id),
            {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "owner_id": project.owner_id,
                "created_at": project.created_at.isoformat(),
            },
            ttl_seconds=settings.project_cache_ttl_seconds,
        )
