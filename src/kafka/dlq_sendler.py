import logging
from datetime import UTC, datetime
from typing import Any

from src.kafka.kafka_producer import KafkaProducerClient


class DLQSender:
    def __init__(
        self,
        kafka_producer: KafkaProducerClient,
        dlq_topic: str
    ) -> None:
        self.kafka_producer = kafka_producer
        self.dlq_topic = dlq_topic
        self.logger = logging.getLogger(self.__class__.__name__)

    async def send_to_dlq(
        self,
        original_topic: str,
        original_payload: dict[str, Any],
        original_partition_key: str,
        original_headers: dict[str, str] | None,
        offset: int,
        error_message: str,
        is_retryable: bool,
    ) -> None:

        dlq_payload = {
            "original_topic": original_topic,
            "original_payload": original_payload,
            "original_headers": original_headers,
            "original_partition_key": original_partition_key,
            "original_offset": offset,
            "error": {
                "message": error_message,
                "is_retryable": is_retryable,
                "timestamp": datetime.now(UTC).isoformat(),
            },
        }

        try:
            await self.kafka_producer.send_message(
                topic=self.dlq_topic,
                value=dlq_payload,
                key=original_partition_key,
                headers={
                    "original-topic": original_topic,
                    "is-retryable": str(is_retryable).lower(),
                },
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
            raise
