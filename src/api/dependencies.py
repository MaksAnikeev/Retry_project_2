from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import async_session_factory
from src.repositories.report_rep import ReportRepository
from src.services.report_service import ReportService


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_report_rep(session: SessionDep) -> ReportRepository:
    return ReportRepository(session=session)

ReportRepDep = Annotated[ReportRepository, Depends(get_report_rep)]


def get_report_service(
    report_rep: ReportRepDep,
) -> ReportService:
    return ReportService(
        report_rep=report_rep,
    )

ReportServiceDep = Annotated[ReportService, Depends(get_report_service)]
