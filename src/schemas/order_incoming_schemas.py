import uuid
from pydantic import BaseModel, Field

from src.schemas.kafka_schemas import BaseKafkaHeadersSchema


class OrderPayloadSchema(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID = Field(..., description="Ид пользователя, создавшего заказ")
    product_name: str = Field(
        ...,
        max_length=100,
        description="Название продукта",
    )
    description: str | None = Field(
        None,
        description="Описание продукта"
    )
    price: int = Field(
        ...,
        ge=0,
        description="Цена продукта",
    )
    quantity: int = Field(
        ...,
        gt=0,
        description="Количество единиц продукта",
    )


class IncomingOrderHeadersSchema(BaseKafkaHeadersSchema):
    event_type: str
    aggregate_type: str = "Order"
    event_id: uuid.UUID = Field(..., description="Обязательный ID события")
    content_type: str = "application/json"
    correlation_id: str | None = None
    retry_count: int = Field(default=0, ge=0)


class IncomingOrderMessage(BaseModel):
    headers: IncomingOrderHeadersSchema
    payload: OrderPayloadSchema
    topic: str
    partition_key: str | None = None
    offset: int

class DeliveryPayloadSchema(BaseModel):
    user_id: uuid.UUID
    product_name: str
    description: str | None = None
    price: int
    quantity: int
    event_id: uuid.UUID