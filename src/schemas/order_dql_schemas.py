from pydantic import BaseModel

from src.schemas.dql_schemas import DqlErrorSchema, DqlHeadersSchema
from src.schemas.kafka_schemas import BaseKafkaHeadersSchema, BaseKafkaMessageSchema
from src.schemas.order_incoming_schemas import OrderPayloadSchema, IncomingOrderHeadersSchema


class OrderKafkaMessage(BaseKafkaMessageSchema):
    payload: OrderPayloadSchema
    headers: IncomingOrderHeadersSchema


class DqlOrderMessageSchema(BaseModel):
    original_topic: str
    original_payload: dict
    original_headers: dict[str, str]
    original_partition_key: str
    original_offset: int
    error: DqlErrorSchema


class DqlOrderKafkaMessage(BaseKafkaMessageSchema):
    payload: DqlOrderMessageSchema
    headers: DqlHeadersSchema


