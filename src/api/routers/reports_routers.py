import uuid
from typing import List

from fastapi import APIRouter

from src.api.dependencies import ReportServiceDep
from src.schemas.reports_schemas import ReportGetSchemas, TaskAPIGetSchemas

router = APIRouter(prefix="/reports", tags=["Отчеты"])


@router.get("/user", summary="Получить все отчеты по задачам пользователя")
async def get_reports_by_user(
    user_id: uuid.UUID,
    service: ReportServiceDep
) -> List[ReportGetSchemas]:
    reports = await service.get_all_to_user(user_id=user_id)
    return reports


@router.get("/task", summary="Получить все отчеты по задаче")
async def get_reports_by_task(
    task_id: uuid.UUID,
    service: ReportServiceDep
) -> List[ReportGetSchemas]:
    reports = await service.get_all_to_task(task_id=task_id)
    return reports


@router.get("/{id}", summary="Получить отчеты по ид")
async def get_report(
    id: int,
    service: ReportServiceDep
) -> ReportGetSchemas:
    report = await service.get_one(id=id)
    return report

@router.post("", summary="Добавить отчет на задачу")
async def add_report(
    task_info: TaskAPIGetSchemas,
    service: ReportServiceDep
) -> ReportGetSchemas:
    report = await service.add_report(task_info)
    return report


@router.delete("/{report_id}", summary="Удалить отчет по ИД")
async def del_over_task(
    report_id: int,
    service: ReportServiceDep
) -> dict:
    report = await service.delete(id=report_id)
    return {
    "status": "OK",
    "description": f"Отчет с ид {report.id} удален.",
    "delete_task_info": report,
    }