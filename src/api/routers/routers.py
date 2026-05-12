from fastapi import FastAPI
from src.api.routers.over_task_routers import router as over_task_router


def init_routers(app_: FastAPI) -> None:
    app_.include_router(over_task_router)