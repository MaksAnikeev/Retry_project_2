from datetime import datetime, timedelta, UTC
import logging
import uuid

from src.mappers.delivery_mapper import to_delivery_orm
from src.models.delivery import DeliveryORM
from src.repositories.delivery_rep import DeliveryRepository
from src.database.unit_of_work import UnitOfWork
from src.schemas.delivery_schemas import DeliveryPayloadSchema


class DeliveryService:

    def __init__(
        self,
        uow: UnitOfWork,
        delivery_rep: DeliveryRepository,
    ) -> None:
        self.uow = uow
        self.delivery_rep = delivery_rep

        self.logger = logging.getLogger(self.__class__.__name__)

    async def process_delivery_message(
        self,
        payload_schema: DeliveryPayloadSchema,
    ) -> uuid.UUID | None:
        delivery_orm = to_delivery_orm(payload_schema=payload_schema)
        self._enrich_delivery(delivery_orm)
        async with self.uow:
            delivery_id = await self.delivery_rep.create_delivery_report(delivery_orm=delivery_orm)
            if delivery_id is None:
                self.logger.info(
                    "Delivery already exists (idempotency check passed)",
                    extra={"event_id": str(payload_schema.event_id)},
                )
                return None

            self.logger.debug(
                "Delivery created successfully",
                extra={
                    "delivery_id": str(delivery_id),
                    "event_id": str(payload_schema.event_id),
                },
            )

            return delivery_id

    def _enrich_delivery(self, delivery_orm: DeliveryORM) -> None:
        delivery_orm.status = "delivery"
        delivery_orm.driver_id = uuid.uuid4()
        delivery_orm.delivery_to = datetime.now(UTC) + timedelta(hours=2)
