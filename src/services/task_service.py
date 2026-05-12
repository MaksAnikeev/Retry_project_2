from datetime import date, timedelta
import logging
from typing import List

import aiohttp
from aiohttp import ClientConnectorError, ClientTimeout, ServerDisconnectedError, ClientConnectionError, ClientOSError
from asyncio import TimeoutError as AsyncTimeoutError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.config import settings
from src.exceptions import UserNotFoundException
from src.retry_logic.retry_client import retry_standard
from src.schemas.over_tasks_schemas import (
    TaskCreateSchemas,
    TaskAPIGetSchemas
)
from src.services.base_service import BaseService
from src.services.http_client import TaskServiceClient

logger = logging.getLogger(__name__)


class TaskService(BaseService):
    async def get_all_with_parameters(self, user_id: int) -> list[TaskCreateSchemas]:
        await self.check_user_or_task_exists(user_id=user_id)
        tasks = await self.db.tasks.get_all_with_parameters(user_id=user_id)
        return tasks


    async def get_one(
        self,
        user_id: int,
        task_id: int,
    ) -> TaskCreateSchemas:

        await self.check_user_or_task_exists(user_id=user_id, task_id=task_id)
        task = await self.db.tasks.get_one(
            id=task_id, user_id=user_id
        )
        return task


    async def get_unrealized_tasks_from_external(
        self,
        user_id: int,
    ) -> list[TaskAPIGetSchemas]:
        """
        Получить невыполненные задачи из внешнего сервиса.
        """

        if not self.http_client:
            raise RuntimeError("HTTP client not initialized")

        session = await self.http_client.get_session()
        url = f"{self.http_client.base_url}/tasks/{user_id}/unrealized_tasks"

        async with session.get(url) as response:
            if response.status == 404:
                raise UserNotFoundException(f"User {user_id} not found in external service")
            response.raise_for_status()
            data = await response.json()
            tasks = [TaskAPIGetSchemas(**task) for task in data.get("tasks", [])]
            return tasks

    async def get_unrealized_tasks_from_external_with_retry(self, user_id: int) -> list[TaskAPIGetSchemas]:
        """
        Получить невыполненные задачи из внешнего сервиса с использованием retry и Circuit Breaker

        Порядок вызова:
        1. Circuit Breaker проверяет состояние
        2. Если CLOSED/HALF_OPEN → выполняет запрос с retry
        3. При успехе → сбрасывает счётчик ошибок
        4. При ошибке → увеличивает счётчик, может открыть цепь
        """
        return await self._circuit_breaker.call(
            retry_standard(self.get_unrealized_tasks_from_external),
            user_id
        )

    async def get_overdue_tasks(self, user_id: int) -> List[TaskCreateSchemas]:
        tasks = await self.get_unrealized_tasks_from_external_with_retry(user_id)

        today = date.today()
        overdue_tasks = []
        try:
            existed_tasks_overdue = await self.db.tasks.get_all_with_parameters(user_id=user_id)
            existed_tasks_overdue_ids = {task.id for task in existed_tasks_overdue}
        except UserNotFoundException:
            existed_tasks_overdue_ids = []

        for task in tasks:
            if task.id not in existed_tasks_overdue_ids and task.finish_date < today:
                overdue_tasks.append(
                    TaskCreateSchemas(
                        **task.model_dump(),
                        cause_overdue="Task deadline exceeded",
                        new_finish_date=today + timedelta(days=2),
                    )
                )

        return overdue_tasks

    async def add_overdue_tasks(self, user_id: int) -> List[TaskCreateSchemas]:
        tasks_overdue = await self.get_overdue_tasks(user_id=user_id)
        added_tasks = []
        for task in tasks_overdue:
            task_info = TaskCreateSchemas(
                    **task.model_dump(),
                )
            task: TaskCreateSchemas = await self.db.tasks.add(task_info)
            added_tasks.append(task)

        await self.db.commit()
        return added_tasks

    async def delete(
        self,
        user_id: int,
        task_id: int,
    ) -> TaskCreateSchemas:

        await self.check_user_or_task_exists(user_id=user_id, task_id=task_id)
        task = await self.db.tasks.delete(id=task_id, user_id=user_id)
        return task