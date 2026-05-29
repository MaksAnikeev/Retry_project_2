import uuid
from datetime import date
import logging

from src.exceptions.exceptions import ObjectNotFoundHTTPException, ObjectNotFoundException
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


    async def check_user_exists(self, user_id: uuid.UUID) -> bool:
        user = await self.report_rep.get_all(user_id=user_id)
        if not user:
            raise ObjectNotFoundHTTPException

    async def check_task_exists(self, task_id: uuid.UUID) -> bool:
        task = await self.report_rep.get_all(task_id=task_id)
        if not task:
            raise ObjectNotFoundHTTPException

    async def get_all_to_user(self, user_id: uuid.UUID) -> list[ReportGetSchemas]:
        await self.check_user_exists(user_id=user_id)
        reports = await self.report_rep.get_all_with_parameters(user_id=user_id)
        return reports

    async def get_all_to_task(self, task_id: uuid.UUID) -> list[ReportGetSchemas]:
        await self.check_task_exists(task_id=task_id)
        reports = await self.report_rep.get_all_with_parameters(task_id=task_id)
        return reports

    async def get_one(
        self,
        id: int,
    ) -> ReportGetSchemas:
        try:
            report = await self.report_rep.one_or_none(id=id)
        except ObjectNotFoundException:
            raise ObjectNotFoundHTTPException
        return report

    # async def get_unrealized_tasks_from_external_with_retry(self, user_id: int) -> list[TaskAPIGetSchemas]:
    #     """
    #     Получить невыполненные задачи из внешнего сервиса с использованием retry и Circuit Breaker
    #
    #     Порядок вызова:
    #     1. Circuit Breaker проверяет состояние
    #     2. Если CLOSED/HALF_OPEN → выполняет запрос с retry
    #     3. При успехе → сбрасывает счётчик ошибок
    #     4. При ошибке → увеличивает счётчик, может открыть цепь
    #     """
    #     return await self._circuit_breaker.call(
    #         retry_standard(self.http_client.get_unrealized_tasks),
    #         user_id
    #     )

    # async def get_overdue_tasks(self, user_id: int) -> List[TaskCreateSchemas]:
    #     tasks = await self.get_unrealized_tasks_from_external_with_retry(user_id)
    #
    #     today = date.today()
    #     overdue_tasks = []
    #     try:
    #         existed_tasks_overdue = await self.db.tasks.get_all_with_parameters(user_id=user_id)
    #         existed_tasks_overdue_ids = {task.id for task in existed_tasks_overdue}
    #     except UserNotFoundException:
    #         existed_tasks_overdue_ids = []
    #
    #     for task in tasks:
    #         if task.id not in existed_tasks_overdue_ids and task.finish_date < today:
    #             overdue_tasks.append(
    #                 TaskCreateSchemas(
    #                     **task.model_dump(),
    #                     cause_overdue="Task deadline exceeded",
    #                     new_finish_date=today + timedelta(days=2),
    #                 )
    #             )
    #
    #     return overdue_tasks

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

        report_info = ReportCreateSchemas(
            task_id=task_info.task_id,
            user_id=task_info.user_id,
            complexity=complexity,
            estimated_hours=estimated_hours,
            priority=priority)

        report = await self.report_rep.add(report_info)
        await self.report_rep.commit()
        return report

    async def delete(
        self,
        id: int,
    ) -> ReportGetSchemas:
        try:
            report = await self.report_rep.delete(id=id)
        except ObjectNotFoundException:
            raise ObjectNotFoundHTTPException
        await self.report_rep.commit()
        return report