import asyncio
import json
import logging

import aio_pika
from aio_pika import ExchangeType

from app.core.config import settings
from app.messaging.rabbitmq import EVENT_EXCHANGE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def consume() -> None:
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    async with connection:
        channel = await connection.channel()
        exchange = await channel.declare_exchange(
            EVENT_EXCHANGE,
            ExchangeType.TOPIC,
            durable=True,
        )
        queue = await channel.declare_queue(
            "taskflow.notifications",
            durable=True,
        )
        await queue.bind(exchange, routing_key="project.created")

        logger.info("RabbitMQ worker is waiting for messages")
        async with queue.iterator() as messages:
            async for message in messages:
                async with message.process(requeue=True):
                    payload = json.loads(message.body)
                    logger.info("Received project.created event: %s", payload)


if __name__ == "__main__":
    asyncio.run(consume())
