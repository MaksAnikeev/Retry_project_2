import aiohttp
from typing import Optional
from src.config import settings


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

    async def close(self):
        """Закрытие при shutdown"""
        if self._session and not self._session.closed:
            await self._session.close()