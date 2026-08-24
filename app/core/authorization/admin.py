from app.core.authorization.base import ProjectAuthorizationStrategy
from app.models.project import Project
from app.models.user import User


class AdminAuthorizationStrategy(
    ProjectAuthorizationStrategy
):

    def can_access(
        self,
        project: Project,
        user: User,
    ) -> bool:
        return user.role == "admin"

    def can_update(
        self,
        project: Project,
        user: User,
    ) -> bool:
        return user.role == "admin"

    def can_delete(
        self,
        project: Project,
        user: User,
    ) -> bool:
        return user.role == "admin"

    def can_list_all(self, user: User) -> bool:
        return user.role == "admin"
