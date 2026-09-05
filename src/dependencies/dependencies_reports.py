from typing import Annotated

from fastapi import Depends

from src.database.db import SessionDep
from src.dependencies.dependencies_uow import UowDep
from src.repositories.report_rep import ReportRepository
from src.services.report_service import ReportService


def get_report_rep(session: SessionDep) -> ReportRepository:
    return ReportRepository(session=session)

ReportRepDep = Annotated[ReportRepository, Depends(get_report_rep)]


def get_report_service(
    report_rep: ReportRepDep,
    uow: UowDep,
) -> ReportService:
    return ReportService(
        report_rep=report_rep,
        uow=uow,
    )

ReportServiceDep = Annotated[ReportService, Depends(get_report_service)]
