from sqlalchemy.dialects.postgresql import insert
from src.models.reports import ReportsORM
from src.repositories.base import BaseRepository


class ReportRepository(BaseRepository[ReportsORM]):
    model = ReportsORM

    async def add_bulk(self, reports_data: list[dict]) -> list[ReportsORM]:
        stmt = insert(self.model).values(reports_data)

        stmt = stmt.on_conflict_do_update(
            index_elements=["task_id"],
            set_={
                "complexity": stmt.excluded.complexity,
                "estimated_hours": stmt.excluded.estimated_hours,
                "priority": stmt.excluded.priority,
                "user_id": stmt.excluded.user_id,
            },
        )

        stmt = stmt.returning(self.model)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
