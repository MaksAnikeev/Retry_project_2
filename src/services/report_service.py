import uuid
from datetime import date
import logging

from src.schemas.reports_schemas import ReportDeletedResponse

from src.repositories.unit_of_work import UnitOfWork
from src.exceptions import ObjectNotFoundException
from src.repositories.report_rep import ReportRepository
from src.schemas.reports_schemas import (
    TaskAPIGetSchemas,
    ReportGetSchemas,
    Complexity,
    Priority,
    ReportCreateSchemas
)

logger = logging.getLogger(__name__)


class ReportService:

    def __init__(
        self,
        report_rep: ReportRepository,
        uow: UnitOfWork,
    ) -> None:
        self.report_rep = report_rep
        self.uow = uow

        self.logger = logging.getLogger(self.__class__.__name__)


    async def check_user_exists(self, user_id: uuid.UUID) -> None:
        user = await self.report_rep.get_all_with_any_parameters(user_id=user_id)
        if not user:
            self.logger.warning("User not found", extra={"user_id": str(user_id)})
            raise ObjectNotFoundException(f"User with user_id {user_id} not found")

    async def check_task_exists(self, task_id: uuid.UUID) -> None:
        task = await self.report_rep.get_all_with_any_parameters(task_id=task_id)
        if not task:
            self.logger.warning("Task not found", extra={"task_id": str(task_id)})
            raise ObjectNotFoundException(f"Task with task_id:{task_id} not found")

    async def check_report_exists(self, report_id: int) -> None:
        report = await self.report_rep.one_or_none(id=report_id)
        if not report:
            self.logger.warning("Report not found", extra={"report_id": report_id})
            raise ObjectNotFoundException(f"Report with report_id {report_id} not found")

    async def get_all_to_user(self, user_id: uuid.UUID) -> list[ReportGetSchemas]:
        await self.check_user_exists(user_id=user_id)
        reports = await self.report_rep.get_all_with_any_parameters(user_id=user_id)
        self.logger.debug(
            "Reports retrieved for user",
            extra={"user_id": str(user_id), "count": len(reports)}
        )
        return [ReportGetSchemas.model_validate(report, from_attributes=True) for report in reports]

    async def get_all_to_task(self, task_id: uuid.UUID) -> list[ReportGetSchemas]:
        await self.check_task_exists(task_id=task_id)
        reports = await self.report_rep.get_all_with_any_parameters(task_id=task_id)
        self.logger.debug(
            "Reports retrieved for task",
            extra={"task_id": str(task_id), "count": len(reports)}
        )
        return [ReportGetSchemas.model_validate(report, from_attributes=True) for report in reports]

    async def get_one(
        self,
        report_id: int,
    ) -> ReportGetSchemas:
        report = await self.report_rep.one_or_none(id=report_id)
        if not report:
            self.logger.warning("Report not found", extra={"report_id": report_id})
            raise ObjectNotFoundException(f"Report with report_id {report_id} not found")
        self.logger.debug("Report retrieved successfully", extra={"report_id": report_id})
        return ReportGetSchemas.model_validate(report, from_attributes=True)

    async def add_reports_batch(
        self,
        tasks_info: list[TaskAPIGetSchemas],
    ) -> list[ReportGetSchemas]:
        self.logger.info("Starting add_reports_batch")

        if not tasks_info:
            self.logger.info("Finish add_reports_batch. No tasks found")
            return []

        reports_to_create = []

        for task_info in tasks_info:
            self.logger.info(
                "Starting calculate task",
                extra={
                    "task_id": str(task_info.task_id),
                    "user_id": str(task_info.user_id),
                    "finish_date": str(task_info.finish_date),
                }
            )
            days_left = (task_info.finish_date - date.today()).days
            text_len = len(task_info.description or task_info.title)

            if text_len > 100:
                complexity, estimated_hours = Complexity.HARD, 8.0
            elif text_len > 30:
                complexity, estimated_hours = Complexity.NORMAL, 4.0
            else:
                complexity, estimated_hours = Complexity.EASY, 2.0

            priority = (
                Priority.URGENT if days_left <= 1
                else Priority.HIGH if days_left <= 3
                else Priority.MEDIUM
            )
            self.logger.debug(
                "Report parameters calculated",
                extra={
                    "task_id": str(task_info.task_id),
                    "complexity": complexity,
                    "estimated_hours": estimated_hours,
                    "priority": priority,
                    "days_left": days_left,
                    "text_len": text_len,
                }
            )

            reports_to_create.append({
                "task_id": task_info.task_id,
                "user_id": task_info.user_id,
                "complexity": complexity,
                "estimated_hours": estimated_hours,
                "priority": priority,
            })
        async with self.uow:
            reports = await self.report_rep.add_bulk(reports_to_create)
            self.logger.info(
                "Reports created successfully",
                extra={
                    "quantity_reports": len(reports),
                }
            )
            return [ReportGetSchemas.model_validate(r, from_attributes=True) for r in reports]

    async def delete(
        self,
        report_id: int,
    ) -> ReportGetSchemas:
        await self.check_report_exists(report_id=report_id)
        async with self.uow:
            report = await self.report_rep.delete(id=report_id)
            report_dto = ReportGetSchemas.model_validate(report, from_attributes=True)
        self.logger.info(
            "Report deleted successfully",
            extra={"report_id": report_id}
        )
        return ReportDeletedResponse(
            status="OK",
            description=f"Отчет с ид {report_dto.id} удален.",
            delete_report_info=report_dto,
        )
