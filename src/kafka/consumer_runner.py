import asyncio
import logging

from src.config import settings
from src.dependencies.dependencies_delivery import delivery_service_factory
from src.kafka.dlq_sendler import DLQSender
from src.kafka.kafka_consumer import OrderConsumer


async def run_consumer_background() -> None:
    logging.info("Starting delivery consumer...")

    dlq_sender = DLQSender(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)
    await dlq_sender.start()

    consumer = OrderConsumer(
        delivery_service_factory=delivery_service_factory,
        dlq_sender=dlq_sender,
    )

    try:
        await consumer.run()
    except asyncio.CancelledError:
        logging.info("Consumer task cancelled")
    finally:
        await dlq_sender.stop()
        logging.info("Consumer stopped")
