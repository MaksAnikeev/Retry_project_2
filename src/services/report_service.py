import uuid
from datetime import date
import logging

from asyncpg import UniqueViolationError, ForeignKeyViolationError
from sqlalchemy.exc import IntegrityError

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
    ) -> None:
        self.report_rep = report_rep


    async def check_user_exists(self, user_id: uuid.UUID) -> None:
        user = await self.report_rep.get_all_with_any_parameters(user_id=user_id)
        if not user:
            logging.warning(f"User with id {user_id} not found")
            raise ObjectNotFoundException

    async def check_task_exists(self, task_id: uuid.UUID) -> None:
        task = await self.report_rep.get_all_with_any_parameters(task_id=task_id)
        if not task:
            logging.warning(f"Task with id {task_id} not found")
            raise ObjectNotFoundException

    async def check_report_exists(self, report_id: int) -> None:
        report = await self.report_rep.one_or_none(id=report_id)
        if not report:
            logging.warning(f"Report with id {report_id} not found")
            raise ObjectNotFoundException

    async def get_all_to_user(self, user_id: uuid.UUID) -> list[ReportGetSchemas]:
        await self.check_user_exists(user_id=user_id)
        reports = await self.report_rep.get_all_with_any_parameters(user_id=user_id)
        return reports

    async def get_all_to_task(self, task_id: uuid.UUID) -> list[ReportGetSchemas]:
        await self.check_task_exists(task_id=task_id)
        reports = await self.report_rep.get_all_with_any_parameters(task_id=task_id)
        return reports

    async def get_one(
        self,
        report_id: int,
    ) -> ReportGetSchemas:
        report = await self.report_rep.one_or_none(id=report_id)
        if not report:
            logging.warning(f"Report with id {report_id} not found")
            raise ObjectNotFoundException
        return report

    async def add_report(
        self,
        task_info: TaskAPIGetSchemas
    ) -> ReportGetSchemas:
        days_left = (task_info.finish_date - date.today()).days
        text_len = len(task_info.description or task_info.title)


        if text_len > 100:
            complexity = Complexity.HARD
            estimated_hours = 8.0
        elif text_len > 30:
            complexity = Complexity.NORMAL
            estimated_hours = 4.0
        else:
            complexity = Complexity.EASY
            estimated_hours = 2.0


        priority = (Priority.URGENT if days_left <= 1
                    else Priority.HIGH if days_left <= 3
                    else Priority.MEDIUM)

        try:
            report_info = ReportCreateSchemas(
                task_id=task_info.task_id,
                user_id=task_info.user_id,
                complexity=complexity,
                estimated_hours=estimated_hours,
                priority=priority)

            report = await self.report_rep.add(report_info)

        except IntegrityError as ex:
            await self.report_rep.rollback()
            logging.error(f"Unknown integrity error: {ex}")

        except Exception as e:
            await self.report_rep.rollback()
            logging.error(f"{task_info.title} \n {str(e)}")

        await self.report_rep.commit()
        return report

    async def delete(
        self,
        report_id: int,
    ) -> ReportGetSchemas:
        await self.check_report_exists(report_id=report_id)
        report = await self.report_rep.delete(id=id)
        await self.report_rep.commit()
        return report
