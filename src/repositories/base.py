from typing import Any, Generic, TypeVar, Type

from sqlalchemy import select, insert, delete, ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession

Model = TypeVar("Model")
Schema = TypeVar("Schema")

class BaseRepository(Generic[Model, Schema]):
    model: Type[Model]
    session: AsyncSession

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_with_any_parameters(
        self,
        *filters: ColumnElement[bool],
        **filter_by: Any
    ) -> list[Model]:
        query = select(self.model).filter(*filters).filter_by(**filter_by)
        query_result = await self.session.execute(query)
        return list(query_result.scalars().all())

    async def one_or_none(self, **filters: Any) -> Model | None:
        query = select(self.model).filter_by(**filters)
        query_result = await self.session.execute(query)
        result = query_result.scalars().one_or_none()
        return result

    async def delete(self, **filters: Any) -> Model | None:
        stmt = (
            delete(self.model)
            .filter_by(**filters)
            .returning(self.model)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
