from src.models.delivery import DeliveryORM
from src.schemas.delivery_schemas import DeliveryPayloadSchema


def to_delivery_orm(payload: dict) -> DeliveryORM:
    payload_validated = DeliveryPayloadSchema.model_validate(payload)
    return DeliveryORM(
        is_deleted=False,
        **payload_validated.model_dump()
    )
