from fastapi import FastAPI
from src.api.routers.tasks_routers import router as tasks_router


def init_routers(app_: FastAPI) -> None:
    app_.include_router(tasks_router)