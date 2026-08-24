from app.core.authorization.admin import (
    AdminAuthorizationStrategy,
)
from app.core.authorization.base import (
    ProjectAuthorizationStrategy,
)
from app.core.authorization.user import (
    UserAuthorizationStrategy,
)
from app.models.user import User


def get_project_authorization_strategy(
    user: User,
) -> ProjectAuthorizationStrategy:

    if user.role == "admin":
        return AdminAuthorizationStrategy()

    return UserAuthorizationStrategy()