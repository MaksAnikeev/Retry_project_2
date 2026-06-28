import logging
from typing import Any, Generic, TypeVar, Type

from sqlalchemy import select, insert, update, delete, ColumnElement
from sqlalchemy.exc import IntegrityError
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

    async def add_bulk(self, data_list: list[dict]) -> list[Model]:
        if not data_list:
            return []

        stmt = insert(self.model).values(data_list).returning(self.model)
        result = await self.session.execute(stmt)
        await self.session.flush()
        return list(result.scalars().all())

    async def delete(self, **filters: Any) -> Model:
        query = select(self.model).filter_by(**filters)
        query_result = await self.session.execute(query)
        result = query_result.scalars().one_or_none()
        stmt = (
            delete(self.model).where(self.model.id == result.id).returning(self.model)
        )
        delete_result = await self.session.execute(stmt)
        return delete_result

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
