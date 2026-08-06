import uuid

from pydantic import BaseModel


class DeliveryPayloadSchema(BaseModel):
    user_id: uuid.UUID
    product_name: str
    description: str | None = None
    price: int
    quantity: int