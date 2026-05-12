from fastapi.responses import UJSONResponse
from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi import FastAPI
import sys
import logging
from pathlib import Path
from sqlalchemy import text

from src.api import dependencies
from src.api.routers.routers import init_routers
from src.config import settings
from src.db import async_session_factory_null_pull
from src.services.http_client import TaskServiceClient

sys.path.append(str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO)


def get_app() -> FastAPI:
    """
    Get FastAPI application.
    This is the main constructor of an application.
    :return: application.
    """

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        try:
            async with async_session_factory_null_pull() as session:
                await session.execute(text("SELECT 1"))
                logging.info("Подключение к базе данных успешно проверено")
        except Exception as e:
            logging.critical(
                "Не удалось подключиться к базе данных при старте", exc_info=True
            )
            raise RuntimeError(f"Ошибка подключения к БД: {e}") from e

        # Инициализация клиента — ЧЕРЕЗ МОДУЛЬ
        dependencies._task_client = TaskServiceClient(
            base_url=settings.TASK_SERVICE_URL,
            timeout=30,
        )
        logging.info(f"✅ Client ready: {dependencies._task_client.base_url}")

        yield

        if dependencies._task_client:
            try:
                await dependencies._task_client.close()
            except Exception as e:
                logging.warning(f"Error closing HTTP client: {e}")
            finally:
                dependencies._task_client = None


    app = FastAPI(
        docs_url='/docs',
        openapi_url='/openapi.json',
        default_response_class=UJSONResponse,
        lifespan=lifespan
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=False,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    init_routers(app_=app)

    return app