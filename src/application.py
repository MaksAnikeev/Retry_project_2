import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.api.routers.health_routers import router as health_router
from src.api.routers.reports_routers import router as report_router
from src.config import settings
from src.exceptions import BaseDomainException
from src.exceptions.handlers.handlers import domain_exception_handler
from src.kafka.consumer_runner import run_consumer_background
from src.utils.logging_config import setup_logging

sys.path.append(str(Path(__file__).parent.parent))


logger = logging.getLogger(__name__)
setup_logging(level=settings.LOG_LEVEL)


def _register_routers(app: FastAPI) -> None:
    app.include_router(report_router)
    app.include_router(health_router)

def _register_middlewares(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=False,
        allow_methods=['*'],
        allow_headers=['*'],
    )

def _register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(BaseDomainException, domain_exception_handler)

def get_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        consumer_task = asyncio.create_task(run_consumer_background())
        yield
        consumer_task.cancel()
        try:
            await consumer_task
        except asyncio.CancelledError:
            pass

    app = FastAPI(
        docs_url='/docs',
        openapi_url='/openapi.json',
        lifespan=lifespan
    )
    _register_routers(app)
    _register_middlewares(app)
    _register_exception_handlers(app)
    return app
