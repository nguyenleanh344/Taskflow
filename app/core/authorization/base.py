from abc import ABC, abstractmethod

from app.models.project import Project
from app.models.user import User


class ProjectAuthorizationStrategy(ABC):

    @abstractmethod
    def can_access(
        self,
        project: Project,
        user: User,
    ) -> bool:
        pass

    @abstractmethod
    def can_update(
        self,
        project: Project,
        user: User,
    ) -> bool:
        pass

    @abstractmethod
    def can_delete(
        self,
        project: Project,
        user: User,
    ) -> bool:
        pass

    @abstractmethod
    def can_list_all(self, user: User) -> bool:
        pass
