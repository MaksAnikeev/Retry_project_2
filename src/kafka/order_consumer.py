import asyncio
import base64
import logging
import uuid

from aiokafka import AIOKafkaConsumer, ConsumerRecord

from src.exceptions import ObjectNotFoundException
from src.kafka.dlq_sendler import DLQSender
from src.kafka.error_config import NON_RETRYABLE_ERRORS, RETRYABLE_ERRORS
from src.kafka.kafka_producer import KafkaProducerClient
from src.schemas.delivery_schemas import DeliveryPayloadSchema
from src.services.delivery_service import DeliveryService


class OrderConsumer:

    def __init__(
        self,
        consumer: AIOKafkaConsumer,
        kafka_producer: KafkaProducerClient,
        delivery_service: DeliveryService,
        dlq_sender: DLQSender,
        max_retry_attempts: int = 3
    ) -> None:
        self.consumer = consumer
        self.kafka_producer = kafka_producer
        self.delivery_service = delivery_service
        self.dlq_sender = dlq_sender
        self.max_retry_attempts = max_retry_attempts

        self.logger = logging.getLogger(self.__class__.__name__)

    async def run(self) -> None:
        self.logger.info("Order consumer started")

        try:
            async for message in self.consumer:
                await self._handle_message(message)
        except asyncio.CancelledError:
                self.logger.info("Consumer processing cancelled")
                raise

    async def _handle_message(self, message: ConsumerRecord) -> None:
        if message.value is None:
            self.logger.warning("Tombstone message, skipping")
            await self.consumer.commit()
            return

        try:
            event_id = self._extract_event_id(message)
            data = {**message.value, "event_id": event_id}
            payload_schema = DeliveryPayloadSchema.model_validate(data)

            await self.delivery_service.process_delivery_message(
                payload_schema=payload_schema,
            )
            await self.consumer.commit()

        except RETRYABLE_ERRORS as e:
            await self._handle_error(message, e, is_retryable=True)

        except NON_RETRYABLE_ERRORS as e:
            await self._send_to_dlq(message, e, is_retryable=False)


    def _extract_event_id(self, message: ConsumerRecord) -> uuid.UUID:
        headers = self._extract_headers(message)
        event_id_str = headers.get("event-id")
        if not event_id_str:
            raise ObjectNotFoundException(detail="event-id header not found")
        return uuid.UUID(event_id_str)

    def _extract_headers(self, message: ConsumerRecord) -> dict[str, str]:
        if message.headers is None:
            return {}
        headers = {}
        for key, value in message.headers:
            try:
                headers[key] = value.decode("utf-8")
            except UnicodeDecodeError:
                encoded = base64.b64encode(value).decode("ascii")
                headers[key] = f"base64:{encoded}"
        return headers

    async def _handle_error(
        self,
        message: ConsumerRecord,
        error: Exception,
        is_retryable: bool,
    ) -> None:
        error_message = f"{type(error).__name__}: {str(error)}"
        self.logger.error(
            "Error processing message",
            extra={
                "error": error_message,
                "is_retryable": is_retryable,
                "offset": message.offset,
            },
        )
        retry_count = self._extract_retry_count(message)
        if retry_count >= self.max_retry_attempts:
            await self._send_to_dlq(message, error, is_retryable=True)
            return
        await self._retry_message(message, retry_count + 1)

    def _extract_retry_count(self, message: ConsumerRecord) -> int:
        if not message.headers:
            return 0

        for key, value in message.headers:
            if key == "retry-count":
                try:
                    return int(value.decode("utf-8"))
                except (ValueError, AttributeError):
                    return 0
        return 0

    async def _retry_message(
        self,
        message: ConsumerRecord,
        new_retry_count: int,
    ) -> None:
        headers = dict(message.headers) if message.headers else {}
        headers["retry-count"] = str(new_retry_count).encode("utf-8")

        await self.kafka_producer.send_message(
            topic=message.topic,
            value=message.value,
            key=message.key,
            headers=headers,
        )

        self.logger.info(
            "Message retried",
            extra={
                "topic": message.topic,
                "offset": message.offset,
                "retry_count": new_retry_count,
            },
        )
        await self.consumer.commit()

    async def _send_to_dlq(
        self,
        message: ConsumerRecord,
        error: Exception,
        is_retryable: bool,
    ) -> None:
        payload = message.value if isinstance(message.value, dict) else {"raw": str(message.value)}
        headers = self._extract_headers(message)
        partition_key = (
            message.key.decode("utf-8")
            if isinstance(message.key, bytes)
            else message.key
        )
        error_message = f"{type(error).__name__}: {str(error)}"
        await self.dlq_sender.send_to_dlq(
            original_topic=message.topic,
            original_payload=payload,
            original_partition_key=partition_key,
            original_headers=headers,
            offset=message.offset,
            error_message=error_message,
            is_retryable=is_retryable,
        )
        await self.consumer.commit()
