import uuid
from typing import List

from fastapi import APIRouter

from src.dependencies.dependencies import ReportServiceDep
from src.schemas.reports_schemas import ReportGetSchemas, TaskAPIGetSchemas, ReportDeletedResponse

router = APIRouter(prefix="/reports", tags=["Отчеты"])


@router.get("/user", summary="Получить все отчеты по задачам пользователя")
async def get_reports_by_user(
    user_id: uuid.UUID,
    service: ReportServiceDep
) -> List[ReportGetSchemas]:
    return await service.get_all_to_user(user_id=user_id)


@router.get("/task", summary="Получить все отчеты по задаче")
async def get_reports_by_task(
    task_id: uuid.UUID,
    service: ReportServiceDep
) -> List[ReportGetSchemas]:
    return await service.get_all_to_task(task_id=task_id)


@router.get("/{report_id}", summary="Получить отчеты по ид")
async def get_report(
    report_id: int,
    service: ReportServiceDep
) -> ReportGetSchemas:
    return await service.get_one(report_id=report_id)


@router.post("", summary="Добавить отчет на задачу")
async def add_report(
    tasks_info: list[TaskAPIGetSchemas],
    service: ReportServiceDep
) -> list[ReportGetSchemas]:
    return await service.add_reports_batch(tasks_info)


@router.delete("/{report_id}", summary="Удалить отчет по ИД")
async def del_report(
    report_id: int,
    service: ReportServiceDep
) -> ReportDeletedResponse:
    return await service.delete(report_id=report_id)