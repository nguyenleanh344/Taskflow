from app.core.authorization.base import ProjectAuthorizationStrategy
from app.models.project import Project
from app.models.user import User


class UserAuthorizationStrategy(
    ProjectAuthorizationStrategy
):

    def can_access(
        self,
        project: Project,
        user: User,
    ) -> bool:
        return project.owner_id == user.id

    def can_update(
        self,
        project: Project,
        user: User,
    ) -> bool:
        return project.owner_id == user.id

    def can_delete(
        self,
        project: Project,
        user: User,
    ) -> bool:
        return project.owner_id == user.id

    def can_list_all(self, user: User) -> bool:
        return False
