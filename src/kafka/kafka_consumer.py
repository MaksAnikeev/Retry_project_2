import asyncio
import logging

from aiokafka import AIOKafkaConsumer

from src.exceptions import KafkaConsumerNotStartedError
from src.kafka.config import KafkaConsumerConfig


class KafkaConsumerClient:
    def __init__(
        self,
        topics: list[str],
        bootstrap_servers: str,
        config: KafkaConsumerConfig,
    ) -> None:
        self.topics = topics
        self.bootstrap_servers = bootstrap_servers
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

        self._consumer: AIOKafkaConsumer | None = None
        self._lock = asyncio.Lock()
        self._started = False

    async def start(self) -> None:
        if self._started:
            return

        async with self._lock:
            if self._started:
                return

            consumer_config = self.config.to_consumer()
            consumer = AIOKafkaConsumer(
                *self.topics,
                bootstrap_servers=self.bootstrap_servers,
                **consumer_config,
            )
            try:
                await consumer.start()
            except Exception:
                raise

            self._consumer = consumer
            self._started = True

            self.logger.info(
                "Kafka consumer started",
                extra={
                    "bootstrap_servers": self.bootstrap_servers,
                    "topics": self.topics,
                },
            )

    async def stop(self) -> None:
        async with self._lock:
            if self._consumer is None:
                return
            consumer = self._consumer
            self._consumer = None
            self._started = False

        try:
            await consumer.stop()
            self.logger.info("Kafka consumer stopped")
        except Exception as e:
            self.logger.warning(
                "Error while stopping Kafka consumer",
                extra={"error": str(e)},
            )

    async def commit(self) -> None:
        if self._consumer is None:
            raise KafkaConsumerNotStartedError(
                "Kafka consumer is not started. Call start() first."
            )
        await self._consumer.commit()

    def __aiter__(self):
        if self._consumer is None:
            raise KafkaConsumerNotStartedError(
                "Kafka consumer is not started. Call start() first."
            )
        return self._consumer.__aiter__()

