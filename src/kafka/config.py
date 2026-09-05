from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from src.config import settings


class KafkaProducerConfig(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )
    key_serializer: Callable = Field(
        default=lambda k: (
            k if isinstance(k, bytes)
            else k.encode("utf-8") if k
            else None
        ),
    )
    acks: int = -1
    enable_idempotence: bool = True
    compression_type: str = "gzip"

    def to_producer(self) -> dict:
        return self.model_dump(mode="python", exclude_none=True)

kafka_producer_config = KafkaProducerConfig()


class KafkaConsumerConfig(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )
    key_deserializer: Callable[[bytes], str | None] = Field(
        default=lambda k: k.decode("utf-8") if k else None,
        exclude=True,
    )
    group_id: str = settings.ORDER_CONSUMER_GROUP_ID
    auto_offset_reset: str = Field(
        default="earliest",
        description="earliest | latest | none",
    )
    enable_auto_commit: bool = False
    max_poll_records: int = 100

    def to_consumer(self) -> dict[str, Any]:
        return self.model_dump(mode="python", exclude_none=True)

kafka_consumer_config = KafkaConsumerConfig()
