import aiohttp
from typing import Optional
from src.config import settings
from src.exceptions import UserNotFoundException
from src.schemas.over_tasks_schemas import TaskAPIGetSchemas


class TaskServiceClient:
    """HTTP клиент для внешних вызовов (если сервисов несколько)"""

    def __init__(
            self,
            base_url: str | None = None,
            timeout: int = 30,
    ):
        self.base_url = (base_url or settings.TASK_SERVICE_URL).rstrip("/")
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self._session: Optional[aiohttp.ClientSession] = None

    async def get_session(self) -> aiohttp.ClientSession:
        """Ленивое создание сессии (singleton)"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self._session

    # Вход в контекст: гарантируем, что сессия создана
    async def __aenter__(self) -> "TaskServiceClient":
        await self.get_session()
        return self

    # Выход из контекста: закрываем сессию
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session and not self._session.closed:
            await self._session.close()
        return False

    async def get_unrealized_tasks(self, user_id: int) -> list[TaskAPIGetSchemas]:
        session = await self.get_session()
        url = f"{self.base_url}/tasks/{user_id}/unrealized_tasks"

        async with session.get(url) as response:
            if response.status == 404:
                raise UserNotFoundException(f"User {user_id} not found in external service")

            response.raise_for_status()

            data = await response.json()
            return [TaskAPIGetSchemas(**task) for task in data.get("tasks", [])]