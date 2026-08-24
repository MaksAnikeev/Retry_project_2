import asyncio
import logging

from aiokafka import AIOKafkaConsumer

from src.config import settings
from src.database.db import async_session_factory
from src.database.unit_of_work import UnitOfWork
from src.kafka.config import kafka_consumer_config, kafka_producer_config
from src.kafka.dlq_sendler import DLQSender
from src.kafka.order_consumer import OrderConsumer
from src.kafka.kafka_producer import KafkaProducerClient
from src.repositories.delivery_rep import DeliveryRepository
from src.services.delivery_service import DeliveryService


async def run_consumer_background() -> None:
    logging.info("Starting delivery consumer...")

    kafka_producer = KafkaProducerClient(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        config=kafka_producer_config,
    )
    consumer_config = kafka_consumer_config.to_consumer()
    kafka_consumer = AIOKafkaConsumer(
        settings.ORDER_TOPIC,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        **consumer_config,
    )
    dlq_sender = DLQSender(
        kafka_producer=kafka_producer,
        dlq_topic=settings.DLQ_TOPIC,
    )
    await kafka_producer.start()
    await kafka_consumer.start()

    session = async_session_factory()
    uow = UnitOfWork(session=session)
    delivery_repo = DeliveryRepository(session=session)

    delivery_service = DeliveryService(
        delivery_rep=delivery_repo,
        uow=uow,
    )

    consumer = OrderConsumer(
        consumer=kafka_consumer,
        kafka_producer=kafka_producer,
        delivery_service=delivery_service,
        dlq_sender=dlq_sender,
        max_retry_attempts=settings.MAX_RETRY_ATTEMPTS,
    )
    try:
        await consumer.run()
    except asyncio.CancelledError:
        logging.info("Consumer task cancelled")
        raise
    finally:
        await session.close()
        await kafka_consumer.stop()
        await kafka_producer.stop()
        logging.info("All infrastructure stopped")
