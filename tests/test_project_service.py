import unittest
from datetime import datetime, timezone
from unittest.mock import ANY, AsyncMock, patch

from app.core.unit_of_work import UnitOfWork
from app.exceptions.resources import ProjectForbiddenError, ProjectNotFoundError
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.services.project_service import ProjectService
from redis.exceptions import RedisError


class FakeSession:
    def __init__(self):
        self.commit_count = 0
        self.deleted = []

    async def commit(self):
        self.commit_count += 1

    async def refresh(self, instance):
        return None


class FakeProjectRepository:
    projects = {}
    next_id = 1

    def __init__(self, session):
        self.session = session

    async def create(self, name, description, owner_id):
        project = Project(
            id=type(self).next_id,
            name=name,
            description=description,
            owner_id=owner_id,
        )
        type(self).projects[project.id] = project
        type(self).next_id += 1
        return project

    async def get_by_id(self, project_id):
        return type(self).projects.get(project_id)

    async def list_all(self, offset=0, limit=20):
        projects = list(type(self).projects.values())
        return projects[offset : offset + limit]

    async def list_by_owner(self, owner_id, offset=0, limit=20):
        projects = [
            project
            for project in type(self).projects.values()
            if project.owner_id == owner_id
        ]
        return projects[offset : offset + limit]

    async def count_all(self):
        return len(type(self).projects)

    async def count_by_owner(self, owner_id):
        return sum(
            project.owner_id == owner_id for project in type(self).projects.values()
        )

    async def delete(self, project):
        self.session.deleted.append(project.id)
        type(self).projects.pop(project.id, None)


class ProjectServiceTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        FakeProjectRepository.projects = {}
        FakeProjectRepository.next_id = 1
        self.repository_patcher = patch(
            "app.core.unit_of_work.ProjectRepository",
            FakeProjectRepository,
        )
        self.repository_patcher.start()

        self.session = FakeSession()
        self.service = ProjectService(UnitOfWork(self.session))
        self.user = User(id=1, role="user")
        self.other_user = User(id=2, role="user")
        self.admin = User(id=3, role="admin")

    def tearDown(self):
        self.repository_patcher.stop()

    async def test_create_project_uses_current_user_as_owner(self):
        project = await self.service.create_project(
            ProjectCreate(
                name="TaskFlow",
                description="Backend learning project",
            ),
            self.user,
        )

        self.assertEqual(project.id, 1)
        self.assertEqual(project.owner_id, self.user.id)
        self.assertEqual(project.name, "TaskFlow")
        self.assertEqual(self.session.commit_count, 1)

    async def test_list_returns_only_owned_projects_for_regular_user(self):
        await self.service.create_project(ProjectCreate(name="Mine"), self.user)
        await self.service.create_project(
            ProjectCreate(name="Not mine"),
            self.other_user,
        )

        projects = await self.service.list_projects(self.user)

        self.assertEqual([project.name for project in projects.items], ["Mine"])
        self.assertEqual(projects.total, 1)

    async def test_admin_can_list_all_projects(self):
        await self.service.create_project(ProjectCreate(name="First"), self.user)
        await self.service.create_project(
            ProjectCreate(name="Second"),
            self.other_user,
        )

        projects = await self.service.list_projects(self.admin)

        self.assertEqual(
            [project.name for project in projects.items],
            ["First", "Second"],
        )
        self.assertEqual(projects.total, 2)

    async def test_owner_can_update_project(self):
        project = await self.service.create_project(
            ProjectCreate(name="Before"),
            self.user,
        )

        updated = await self.service.update_project(
            project.id,
            ProjectUpdate(name="After"),
            self.user,
        )

        self.assertEqual(updated.name, "After")
        self.assertEqual(updated.owner_id, self.user.id)
        self.assertEqual(self.session.commit_count, 2)

    async def test_non_owner_cannot_read_update_or_delete_project(self):
        project = await self.service.create_project(
            ProjectCreate(name="Private"),
            self.user,
        )

        with self.assertRaises(ProjectForbiddenError):
            await self.service.get_project(project.id, self.other_user)

        with self.assertRaises(ProjectForbiddenError):
            await self.service.update_project(
                project.id,
                ProjectUpdate(name="Hacked"),
                self.other_user,
            )

        with self.assertRaises(ProjectForbiddenError):
            await self.service.delete_project(project.id, self.other_user)

    async def test_admin_can_access_another_users_project(self):
        project = await self.service.create_project(
            ProjectCreate(name="Admin access"),
            self.user,
        )

        result = await self.service.get_project(project.id, self.admin)

        self.assertEqual(result.id, project.id)

    async def test_owner_can_delete_project(self):
        project = await self.service.create_project(
            ProjectCreate(name="To delete"),
            self.user,
        )

        await self.service.delete_project(project.id, self.user)

        self.assertEqual(self.session.deleted, [project.id])
        with self.assertRaises(ProjectNotFoundError):
            await self.service.get_project(project.id, self.user)

    async def test_missing_project_raises_not_found(self):
        with self.assertRaises(ProjectNotFoundError):
            await self.service.get_project(999, self.user)


class ProjectServiceCacheTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = FakeSession()
        self.repository = AsyncMock()
        self.cache = AsyncMock()
        self.service = ProjectService(UnitOfWork(self.session), self.cache)
        self.service.repository = self.repository
        self.user = User(id=1, role="user")
        self.other_user = User(id=2, role="user")
        self.project = Project(
            id=1,
            name="TaskFlow",
            description="Backend learning project",
            owner_id=1,
            created_at=datetime.now(timezone.utc),
        )

    async def test_get_project_cache_miss_loads_from_repository_and_caches(self):
        self.cache.get_json.return_value = None
        self.repository.get_by_id.return_value = self.project

        result = await self.service.get_project(self.project.id, self.user)

        self.assertEqual(result.id, self.project.id)
        self.cache.get_json.assert_awaited_once_with("project:1")
        self.repository.get_by_id.assert_awaited_once_with(1)
        self.cache.set_json.assert_awaited_once_with(
            "project:1",
            ANY,
            ttl_seconds=ANY,
        )

    async def test_get_project_cache_hit_does_not_query_repository(self):
        self.cache.get_json.return_value = {
            "id": 1,
            "name": "TaskFlow",
            "description": "Backend learning project",
            "owner_id": 1,
            "created_at": self.project.created_at.isoformat(),
        }

        result = await self.service.get_project(self.project.id, self.user)

        self.assertEqual(result.id, self.project.id)
        self.repository.get_by_id.assert_not_awaited()
        self.cache.set_json.assert_not_awaited()

    async def test_cached_project_still_requires_authorization(self):
        self.cache.get_json.return_value = {
            "id": 1,
            "name": "TaskFlow",
            "description": "Backend learning project",
            "owner_id": 1,
            "created_at": self.project.created_at.isoformat(),
        }

        with self.assertRaises(ProjectForbiddenError):
            await self.service.get_project(self.project.id, self.other_user)

        self.repository.get_by_id.assert_not_awaited()

    async def test_update_project_invalidates_cache(self):
        self.repository.get_by_id.return_value = self.project

        await self.service.update_project(
            self.project.id,
            ProjectUpdate(name="Updated"),
            self.user,
        )

        self.cache.delete.assert_awaited_once_with("project:1")

    async def test_delete_project_invalidates_cache(self):
        self.repository.get_by_id.return_value = self.project

        await self.service.delete_project(self.project.id, self.user)

        self.repository.delete.assert_awaited_once_with(self.project)
        self.cache.delete.assert_awaited_once_with("project:1")

    async def test_redis_failure_falls_back_to_database(self):
        self.cache.get_json.side_effect = RedisError()
        self.repository.get_by_id.return_value = self.project

        result = await self.service.get_project(self.project.id, self.user)

        self.assertEqual(result.id, self.project.id)
        self.repository.get_by_id.assert_awaited_once_with(1)


if __name__ == "__main__":
    unittest.main()
