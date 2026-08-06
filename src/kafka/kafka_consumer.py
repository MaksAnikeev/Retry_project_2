import json
import logging
import uuid
from json import JSONDecodeError

from aiokafka import AIOKafkaConsumer, ConsumerRecord
from aiokafka.errors import KafkaError
from sqlalchemy.exc import DBAPIError

from src.config import settings
from src.dependencies.dependencies_delivery import DeliveryServiceFactory
from src.exceptions import ObjectNotFoundException
from src.kafka.dlq_sendler import DLQSender


class OrderConsumer:

    _ERROR_MAPPING: dict[type[Exception], bool] = {
        JSONDecodeError: False,
        KeyError: False,
        ValueError: False,
        DBAPIError: True,
        KafkaError: True,
        ConnectionError: True,
    }

    def __init__(
        self,
        delivery_service_factory: DeliveryServiceFactory,
        dlq_sender: DLQSender,
    ) -> None:
        self.dlq_sender = dlq_sender
        self.logger = logging.getLogger(self.__class__.__name__)
        self.consumer: AIOKafkaConsumer | None = None
        self.dlq_sender = dlq_sender
        self.delivery_service_factory = delivery_service_factory

    async def run(self) -> None:
        self.consumer = AIOKafkaConsumer(
            settings.ORDER_TOPIC,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id=settings.ORDER_CONSUMER_GROUP_ID,
            auto_offset_reset="earliest",
            enable_auto_commit=False,
            max_poll_records=100,
        )

        await self.consumer.start()
        self.logger.info("Order consumer started")

        try:
            async for message in self.consumer:
                await self._handle_message(message)
        finally:
            await self.consumer.stop()

    async def _handle_message(self, message: ConsumerRecord) -> None:
        try:
            delivery_service = await self.delivery_service_factory.create()
            payload = json.loads(message.value.decode("utf-8"))
            event_id = self._extract_event_id(message)
            await delivery_service.process_delivery_message(
                payload=payload,
                event_id=event_id,
            )
            await self.consumer.commit()

        except Exception as e:
            is_retryable = self._get_retryable_flag(e)
            await self._handle_error(message, e, is_retryable)

    def _get_retryable_flag(self, error: Exception) -> bool:
        for error_type, is_retryable in self._ERROR_MAPPING.items():
            if isinstance(error, error_type):
                return is_retryable
        return False

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
            except (UnicodeDecodeError, AttributeError):
                headers[key] = str(value)
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
        try:
            payload = json.loads(message.value.decode("utf-8"))
        except Exception:
            payload = {"raw_value": message.value.decode("utf-8", errors="replace")}

        headers = self._extract_headers(message)

        await self.dlq_sender.send_to_dlq(
            original_topic=message.topic,
            original_payload=payload,
            original_headers=headers,
            error_message=error_message,
            is_retryable=is_retryable,
        )
        if not is_retryable:
            await self.consumer.commit()
