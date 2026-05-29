from fastapi.responses import UJSONResponse
from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi import FastAPI
import sys
import logging
from pathlib import Path
from sqlalchemy import text

from src.api.routers.reports_routers import router as report_router
from src.api.routers.health_routers import router as health_router
from src.db import async_session_factory_null_pull

sys.path.append(str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO)


def get_app() -> FastAPI:
    """
    Get FastAPI application.
    This is the main constructor of an application.
    :return: application.
    """

    app = FastAPI(
        docs_url='/docs',
        openapi_url='/openapi.json',
        default_response_class=UJSONResponse,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=False,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    app.include_router(report_router)
    app.include_router(health_router)

    return app