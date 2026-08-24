from src.models.delivery import DeliveryORM
from src.schemas.delivery_schemas import DeliveryPayloadSchema


def to_delivery_orm(payload_schema: DeliveryPayloadSchema) -> DeliveryORM:
    return DeliveryORM(
        is_deleted=False,
        **payload_schema.model_dump()
    )
