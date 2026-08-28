import unittest
from uuid import uuid4

import httpx

from app.cache.redis import redis_client
from app.core.database import SessionLocal
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models.user import User


class ProjectApiIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.email = f"integration-{uuid4()}@example.com"

        async with SessionLocal() as session:
            user = User(
                email=self.email,
                password_hash=hash_password("integration-password"),
                name="Integration User",
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            self.user_id = user.id

        self.client = httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://testserver",
            headers={"Authorization": f"Bearer {create_access_token(self.user_id)}"},
        )

    async def asyncTearDown(self):
        await self.client.aclose()

    async def test_project_is_persisted_and_cached(self):
        create_response = await self.client.post(
            "/api/v1/projects",
            json={"name": "Integration Project", "description": "CI test"},
        )
        self.assertEqual(create_response.status_code, 201)
        project_id = create_response.json()["id"]
        cache_key = f"project:{project_id}"

        await redis_client.delete(cache_key)

        first_response = await self.client.get(f"/api/v1/projects/{project_id}")
        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(first_response.json()["id"], project_id)
        self.assertIsNotNone(await redis_client.get(cache_key))

        second_response = await self.client.get(f"/api/v1/projects/{project_id}")
        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(second_response.json(), first_response.json())


if __name__ == "__main__":
    unittest.main()
