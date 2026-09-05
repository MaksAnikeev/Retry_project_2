from datetime import datetime

from pydantic import BaseModel

from src.schemas.kafka_schemas import BaseKafkaHeadersSchema


class DqlHeadersSchema(BaseKafkaHeadersSchema):
    original_topic: str
    is_retryable: str


class DqlErrorSchema(BaseModel):
    message: str
    is_retryable: bool
    timestamp: datetime
