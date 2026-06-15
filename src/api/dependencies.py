from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.report_rep import ReportRepository
from src.services.report_service import ReportService

from src.db import get_session

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
