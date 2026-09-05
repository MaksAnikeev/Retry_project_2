import logging

from src.kafka.kafka_producer import KafkaProducerClient
from src.schemas.dql_schemas import DqlHeadersSchema
from src.schemas.order_dql_schemas import DqlOrderKafkaMessage, DqlOrderMessageSchema


class DLQSender:
    def __init__(
        self,
        producer: KafkaProducerClient,
        dlq_topic: str
    ) -> None:
        self.producer = producer
        self.dlq_topic = dlq_topic
        self.logger = logging.getLogger(self.__class__.__name__)

    async def send_to_dlq(
        self,
        dlq_message: DqlOrderMessageSchema,
    ) -> None:
        key=dlq_message.original_partition_key
        dql_headers = DqlHeadersSchema(
            original_topic=dlq_message.original_topic,
            is_retryable=str(dlq_message.error.is_retryable).lower(),
        )
        kafka_message = DqlOrderKafkaMessage(
            topic=self.dlq_topic,
            key=key,
            payload=dlq_message,
            headers=dql_headers,
        )
        try:
            await self.producer.send_message(message=kafka_message)
            self.logger.warning(
                "Message sent to DLQ",
                extra={
                    "original_topic": dlq_message.original_topic,
                    "is_retryable": dlq_message.error.is_retryable,
                    "error": dlq_message.error.message,
                },
            )
        except Exception as e:
            self.logger.exception(
                "Failed to send message to DLQ",
                extra={"error": str(e)},
            )
            raise
