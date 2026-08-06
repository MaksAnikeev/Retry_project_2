import uuid

from sqlalchemy import inspect
from sqlalchemy.dialects.postgresql.dml import insert

from src.models.delivery import DeliveryORM
from src.repositories.base import BaseRepository


class DeliveryRepository(BaseRepository[DeliveryORM]):
    model = DeliveryORM

    async def create_delivery_report(self, delivery_orm: DeliveryORM) -> uuid.UUID | None:
        mapper = inspect(DeliveryORM)
        insert_data = {
            column.key: getattr(delivery_orm, column.key)
            for column in mapper.columns
            if column.server_default is None
        }
        stmt = insert(DeliveryORM).values(**insert_data)
        stmt = stmt.on_conflict_do_nothing(index_elements=["event_id"])
        stmt = stmt.returning(DeliveryORM.id)

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()