from src.models.delivery import DeliveryORM
from src.schemas.delivery_schemas import DeliveryPayloadSchema
from src.schemas.order_incoming_schemas import IncomingOrderMessage


def to_delivery_orm(payload_schema: DeliveryPayloadSchema) -> DeliveryORM:
    return DeliveryORM(
        is_deleted=False,
        **payload_schema.model_dump()
    )


def to_delivery_schema(message_schema: IncomingOrderMessage) -> DeliveryPayloadSchema:
    return DeliveryPayloadSchema(
        user_id=message_schema.payload.user_id,
        product_name=message_schema.payload.product_name,
        description=message_schema.payload.description,
        price=message_schema.payload.price,
        quantity=message_schema.payload.quantity,
        event_id=message_schema.headers.event_id,
    )
