import json
import logging

import aio_pika
from aio_pika import DeliveryMode, ExchangeType, Message

from app.core.config import settings

logger = logging.getLogger(__name__)

EVENT_EXCHANGE = "taskflow.events"


class RabbitMQPublisher:
    async def publish(self, routing_key: str, payload: dict) -> None:
        try:
            connection = await aio_pika.connect_robust(settings.rabbitmq_url)
            async with connection:
                channel = await connection.channel()
                exchange = await channel.declare_exchange(
                    EVENT_EXCHANGE,
                    ExchangeType.TOPIC,
                    durable=True,
                )
                await exchange.publish(
                    Message(
                        body=json.dumps(payload).encode(),
                        content_type="application/json",
                        delivery_mode=DeliveryMode.PERSISTENT,
                    ),
                    routing_key=routing_key,
                )
        except (aio_pika.AMQPError, OSError) as exc:
            logger.warning("RabbitMQ publish failed: %s", exc)


publisher = RabbitMQPublisher()


async def get_rabbitmq_publisher() -> RabbitMQPublisher:
    return publisher
