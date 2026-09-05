import logging

from src.kafka.kafka_producer import KafkaProducerClient
from src.schemas.order_dql_schemas import OrderKafkaMessage
from src.schemas.order_incoming_schemas import IncomingOrderMessage


class RetryPublisher:
    def __init__(self, producer: KafkaProducerClient) -> None:
        self.producer = producer
        self.logger = logging.getLogger(self.__class__.__name__)

    async def publish_retry(
        self,
        incoming: IncomingOrderMessage,
        new_retry_count: int,
    ) -> None:
        updated_headers = incoming.headers.model_copy(
            update={"retry_count": new_retry_count}
        )

        message = OrderKafkaMessage(
            topic=incoming.topic,
            payload=incoming.payload,
            key=incoming.partition_key,
            headers=updated_headers,
        )

        await self.producer.send_message(message=message)

        self.logger.info(
            "Retry message published",
            extra={
                "topic": incoming.topic,
                "original_offset": incoming.offset,
                "retry_count": new_retry_count,
            },
        )
