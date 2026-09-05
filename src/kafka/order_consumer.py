import asyncio
import logging

from aiokafka import ConsumerRecord
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.database.unit_of_work import UnitOfWork
from src.kafka.dlq_sender import DLQSender
from src.kafka.error_config import NON_RETRYABLE_ERRORS, RETRYABLE_ERRORS
from src.kafka.kafka_consumer import KafkaConsumerClient
from src.kafka.retry_publisher import RetryPublisher
from src.mappers.delivery_mapper import to_delivery_schema
from src.mappers.kafka_mapper import decode_key, to_headers_dict, to_payload_dict
from src.mappers.order_massage_mapper import (
    to_order_dql_message,
)
from src.repositories.delivery_rep import DeliveryRepository
from src.schemas.order_incoming_schemas import (
    IncomingOrderHeadersSchema,
    IncomingOrderMessage,
    OrderPayloadSchema,
)
from src.services.delivery_service import DeliveryService


class OrderConsumer:

    def __init__(
        self,
        consumer: KafkaConsumerClient,
        retry_publisher: RetryPublisher,
        dlq_sender: DLQSender,
        max_retry_attempts: int,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        self.consumer = consumer
        self.retry_publisher = retry_publisher
        self.dlq_sender = dlq_sender
        self.max_retry_attempts = max_retry_attempts
        self.session_factory = session_factory

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
            incoming = self._parse_incoming_message(message)
        except (ValidationError, ValueError) as e:
            await self._send_to_dlq(message, e, is_retryable=False)
            return

        async with self.session_factory() as session:
            uow = UnitOfWork(session=session)
            repo = DeliveryRepository(session=session)
            service = DeliveryService(delivery_rep=repo, uow=uow)

            try:
                payload_schema = to_delivery_schema(message_schema=incoming)

                async with uow:
                    await service.process_delivery_message(
                        payload_schema=payload_schema,
                    )
                await self.consumer.commit()

            except RETRYABLE_ERRORS as e:
                await self._handle_error(message, e, incoming, is_retryable=True)

            except NON_RETRYABLE_ERRORS as e:
                await self._send_to_dlq(message, e, is_retryable=False)


    def _parse_incoming_message(
        self,
        message: ConsumerRecord,
    ) -> IncomingOrderMessage:
        raw_headers = to_headers_dict(message.headers)
        headers_schema = IncomingOrderHeadersSchema.model_validate(raw_headers)
        payload_dict = to_payload_dict(message.value)
        payload_schema = OrderPayloadSchema.model_validate(payload_dict)
        return IncomingOrderMessage(
            headers=headers_schema,
            payload=payload_schema,
            topic=message.topic,
            partition_key=decode_key(message.key),
            offset=message.offset,
        )

    async def _handle_error(
        self,
        message: ConsumerRecord,
        error: Exception,
        incoming: IncomingOrderMessage,
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
        retry_count = incoming.headers.retry_count
        if retry_count >= self.max_retry_attempts:
            await self._send_to_dlq(message, error, is_retryable=True)
            return
        await self.retry_publisher.publish_retry(
            incoming=incoming,
            new_retry_count=retry_count + 1,
        )
        await self.consumer.commit()

    async def _send_to_dlq(
        self,
        record: ConsumerRecord,
        error: Exception,
        is_retryable: bool,
    ) -> None:
        dlq_message = to_order_dql_message(
            record=record,
            error=error,
            is_retryable=is_retryable)
        await self.dlq_sender.send_to_dlq(dlq_message=dlq_message)
        await self.consumer.commit()
