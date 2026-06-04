import uuid
from typing import List

from fastapi import APIRouter

from src.api.dependencies import ReportServiceDep
from src.schemas.reports_schemas import ReportGetSchemas, TaskAPIGetSchemas, ReportDeletedResponse
from src.utils.logging_decorator import log

router = APIRouter(prefix="/reports", tags=["Отчеты"])


@router.get("/user", summary="Получить все отчеты по задачам пользователя")
@log("get_reports_by_user")
async def get_reports_by_user(
    user_id: uuid.UUID,
    service: ReportServiceDep
) -> List[ReportGetSchemas]:
    reports = await service.get_all_to_user(user_id=user_id)
    return reports


@router.get("/task", summary="Получить все отчеты по задаче")
@log("get_reports_by_task")
async def get_reports_by_task(
    task_id: uuid.UUID,
    service: ReportServiceDep
) -> List[ReportGetSchemas]:
    reports = await service.get_all_to_task(task_id=task_id)
    return reports


@router.get("/{report_id}", summary="Получить отчеты по ид")
@log("get_report")
async def get_report(
    report_id: int,
    service: ReportServiceDep
) -> ReportGetSchemas:
    report = await service.get_one(report_id=report_id)
    return report

@router.post("", summary="Добавить отчет на задачу")
@log("add_report")
async def add_report(
    task_info: TaskAPIGetSchemas,
    service: ReportServiceDep
) -> ReportGetSchemas:
    report = await service.add_report(task_info)
    return report


@router.delete("/{report_id}", summary="Удалить отчет по ИД")
@log("del_report")
async def del_report(
    report_id: int,
    service: ReportServiceDep
) -> ReportDeletedResponse:
    report = await service.delete(report_id=report_id)
    return ReportDeletedResponse(
            status="OK",
            description=f"Отчет с ид {report.id} удален.",
            delete_report_info=report,
        )