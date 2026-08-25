import unittest

from app.core.unit_of_work import UnitOfWork


class FakeSession:
    def __init__(self):
        self.commit_count = 0
        self.rollback_count = 0

    async def commit(self):
        self.commit_count += 1

    async def rollback(self):
        self.rollback_count += 1


class UnitOfWorkTests(unittest.IsolatedAsyncioTestCase):

    async def test_repositories_share_the_same_session(self):
        session = FakeSession()
        uow = UnitOfWork(session)

        self.assertIs(uow.users.session, session)
        self.assertIs(uow.projects.session, session)
        self.assertIs(uow.tasks.session, session)
        self.assertIs(uow.comments.session, session)
        self.assertIs(uow.project_members.session, session)
        self.assertIs(uow.refresh_tokens.session, session)

    async def test_commit_delegates_to_session(self):
        session = FakeSession()
        uow = UnitOfWork(session)

        await uow.commit()

        self.assertEqual(session.commit_count, 1)

    async def test_rollback_delegates_to_session(self):
        session = FakeSession()
        uow = UnitOfWork(session)

        await uow.rollback()

        self.assertEqual(session.rollback_count, 1)

    async def test_context_manager_rolls_back_on_exception(self):
        session = FakeSession()

        with self.assertRaises(RuntimeError):
            async with UnitOfWork(session):
                raise RuntimeError("transaction failed")

        self.assertEqual(session.rollback_count, 1)


if __name__ == "__main__":
    unittest.main()
