from fastapi.responses import UJSONResponse
from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import sys
import logging
from pathlib import Path

from src.api.routers.reports_routers import router as report_router
from src.api.routers.health_routers import router as health_router
from src.exceptions import BaseDomainException
from src.exceptions.handlers import domain_exception_handler

sys.path.append(str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO)


def get_app() -> FastAPI:

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

    app.add_exception_handler(BaseDomainException, domain_exception_handler)

    return app