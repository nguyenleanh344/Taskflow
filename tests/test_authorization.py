import unittest

from app.core.authorization.admin import (
    AdminAuthorizationStrategy,
)
from app.core.authorization.factory import (
    get_project_authorization_strategy,
)
from app.core.authorization.user import (
    UserAuthorizationStrategy,
)
from app.models.project import Project
from app.models.user import User


class AuthorizationStrategyTests(
    unittest.TestCase
):

    def setUp(self):
        self.owner = User(
            id=1,
            role="user",
        )

        self.other_user = User(
            id=2,
            role="user",
        )

        self.admin = User(
            id=3,
            role="admin",
        )

        self.project = Project(
            id=10,
            owner_id=self.owner.id,
            name="TaskFlow",
        )

    def test_owner_can_access_project(self):
        strategy = UserAuthorizationStrategy()

        self.assertTrue(
            strategy.can_access(
                self.project,
                self.owner,
            )
        )

    def test_other_user_cannot_access_project(self):
        strategy = UserAuthorizationStrategy()

        self.assertFalse(
            strategy.can_access(
                self.project,
                self.other_user,
            )
        )

    def test_owner_can_update_project(self):
        strategy = UserAuthorizationStrategy()

        self.assertTrue(
            strategy.can_update(
                self.project,
                self.owner,
            )
        )

    def test_other_user_cannot_update_project(self):
        strategy = UserAuthorizationStrategy()

        self.assertFalse(
            strategy.can_update(
                self.project,
                self.other_user,
            )
        )

    def test_admin_can_access_any_project(self):
        strategy = AdminAuthorizationStrategy()

        self.assertTrue(
            strategy.can_access(
                self.project,
                self.admin,
            )
        )

    def test_admin_can_update_any_project(self):
        strategy = AdminAuthorizationStrategy()

        self.assertTrue(
            strategy.can_update(
                self.project,
                self.admin,
            )
        )

    def test_admin_can_delete_any_project(self):
        strategy = AdminAuthorizationStrategy()

        self.assertTrue(
            strategy.can_delete(
                self.project,
                self.admin,
            )
        )

    def test_admin_strategy_rejects_non_admin_user(self):
        strategy = AdminAuthorizationStrategy()

        self.assertFalse(strategy.can_access(self.project, self.owner))
        self.assertFalse(strategy.can_update(self.project, self.owner))
        self.assertFalse(strategy.can_delete(self.project, self.owner))
        self.assertFalse(strategy.can_list_all(self.owner))

    def test_admin_can_list_all_projects(self):
        strategy = AdminAuthorizationStrategy()

        self.assertTrue(strategy.can_list_all(self.admin))

    def test_user_cannot_list_all_projects(self):
        strategy = UserAuthorizationStrategy()

        self.assertFalse(strategy.can_list_all(self.owner))

    def test_factory_returns_strategy_for_user_role(self):
        self.assertIsInstance(
            get_project_authorization_strategy(self.owner),
            UserAuthorizationStrategy,
        )
        self.assertIsInstance(
            get_project_authorization_strategy(self.admin),
            AdminAuthorizationStrategy,
        )


if __name__ == "__main__":
    unittest.main()
