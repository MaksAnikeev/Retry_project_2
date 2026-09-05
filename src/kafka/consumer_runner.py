import asyncio
import logging

from src.config import settings
from src.database.db import async_session_factory
from src.kafka.config import kafka_consumer_config, kafka_producer_config
from src.kafka.dlq_sender import DLQSender
from src.kafka.kafka_consumer import KafkaConsumerClient
from src.kafka.kafka_producer import KafkaProducerClient
from src.kafka.order_consumer import OrderConsumer
from src.kafka.retry_publisher import RetryPublisher


async def run_consumer_background() -> None:
    logging.info("Starting delivery consumer...")

    producer = KafkaProducerClient(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        config=kafka_producer_config,
    )
    consumer = KafkaConsumerClient(
        topics=[settings.ORDER_TOPIC],
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        config=kafka_consumer_config,
    )
    retry_publisher = RetryPublisher(producer=producer)
    dlq_sender = DLQSender(
        producer=producer,
        dlq_topic=settings.DLQ_TOPIC,
    )
    producer_started = False
    consumer_started = False

    try:
        await producer.start()
        producer_started = True

        await consumer.start()
        consumer_started = True

        order_consumer = OrderConsumer(
            consumer=consumer,
            retry_publisher=retry_publisher,
            dlq_sender=dlq_sender,
            session_factory=async_session_factory,
            max_retry_attempts=settings.MAX_RETRY_ATTEMPTS,
        )
        await order_consumer.run()

    except asyncio.CancelledError:
        logging.info("Consumer task cancelled by signal")
        raise

    except Exception as e:
        logging.exception(
            "Consumer failed with error",
            extra={"error": str(e), "error_type": type(e).__name__},
        )
        raise

    finally:
        if consumer_started:
            try:
                await consumer.stop()
            except Exception as e:
                logging.warning(
                    "Error stopping consumer",
                    extra={"error": str(e)},
                )
        if producer_started:
            try:
                await producer.stop()
            except Exception as e:
                logging.warning(
                    "Error stopping producer",
                    extra={"error": str(e)},
                )

        logging.info("All infrastructure stopped")
