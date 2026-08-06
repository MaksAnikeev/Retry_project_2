import json
import logging
from datetime import UTC, datetime
from typing import Any

from aiokafka import AIOKafkaProducer

from src.config import settings
from src.exceptions import KafkaProducerNotStartedError, KafkaSendError


class DLQSender:
    def __init__(self, bootstrap_servers: str | None = None) -> None:
        self.bootstrap_servers = bootstrap_servers
        self.logger = logging.getLogger(self.__class__.__name__)
        self._producer: AIOKafkaProducer | None = None

    def _get_producer(self) -> AIOKafkaProducer:
        if self._producer is None:
            raise KafkaProducerNotStartedError(
                detail=f"DLQ producer for {self.bootstrap_servers} is not started"
            )
        return self._producer

    async def start(self) -> None:
        if self._producer is not None:
            self.logger.warning("Kafka producer is already started")
            return

        self._producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
            acks="all",
            compression_type="gzip",
        )
        await self._producer.start()
        self.logger.info("DLQ producer started")

    async def stop(self) -> None:
        if self._producer is not None:
            await self._producer.stop()
            self._producer = None
            self.logger.info("DLQ producer stopped")

    async def send_to_dlq(
        self,
        original_topic: str,
        original_payload: dict[str, Any],
        original_headers: dict[str, str] | None,
        error_message: str,
        is_retryable: bool,
    ) -> None:
        _producer = self._get_producer()

        dlq_payload = {
            "original_topic": original_topic,
            "original_payload": original_payload,
            "original_headers": original_headers,
            "error": {
                "message": error_message,
                "is_retryable": is_retryable,
                "timestamp": datetime.now(UTC).isoformat(),
            },
        }

        try:
            await self._producer.send_and_wait(
                topic=settings.DLQ_TOPIC,
                value=dlq_payload,
                key=None,
            )
            self.logger.warning(
                "Message sent to DLQ",
                extra={
                    "original_topic": original_topic,
                    "is_retryable": is_retryable,
                    "error": error_message,
                },
            )
        except Exception as e:
            self.logger.exception(
                "Failed to send message to DLQ",
                extra={"error": str(e)},
            )
            raise KafkaSendError(f"Failed to send to DLQ: {str(e)}") from e
