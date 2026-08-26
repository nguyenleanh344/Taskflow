import json
from typing import Any

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.config import settings


class RedisCache:
    """Small cache adapter with fail-open Redis behavior."""

    def __init__(self, client: Redis):
        self.client = client

    async def get_json(self, key: str) -> dict[str, Any] | None:
        try:
            value = await self.client.get(key)
        except RedisError:
            return None

        if value is None:
            return None

        try:
            return json.loads(value)
        except (TypeError, json.JSONDecodeError):
            return None

    async def set_json(
        self,
        key: str,
        value: dict[str, Any],
        ttl_seconds: int,
    ) -> None:
        try:
            await self.client.set(
                key,
                json.dumps(value),
                ex=ttl_seconds,
            )
        except RedisError:
            return

    async def delete(self, key: str) -> None:
        try:
            await self.client.delete(key)
        except RedisError:
            return


redis_client = Redis.from_url(
    settings.redis_url,
    decode_responses=True,
    protocol=2,
)


async def get_redis() -> RedisCache:
    return RedisCache(redis_client)


async def close_redis() -> None:
    await redis_client.aclose()
