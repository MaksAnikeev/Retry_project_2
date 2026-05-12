from typing import Annotated

from fastapi import Depends, HTTPException

from src.db import async_session_factory
from src.services.http_client import TaskServiceClient
from src.utils.db_manager import DBManager


# Глобальный HTTP клиент (заполняется в lifespan)
_task_client: TaskServiceClient | None = None

def get_task_client() -> TaskServiceClient:
    """Dependency для получения HTTP клиента"""
    if _task_client is None:
        raise HTTPException(
            status_code=503,
            detail="Task Service Client not initialized",
        )
    return _task_client

TaskClientDep = Annotated[TaskServiceClient, Depends(get_task_client)]


async def get_db():
    async with DBManager(session_factory=async_session_factory) as db:
        yield db

DBDep = Annotated[DBManager, Depends(get_db)]
