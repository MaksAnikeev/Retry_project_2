from fastapi import APIRouter, status
from starlette.responses import JSONResponse

from src.api.routers.health.utils import HealthDB
from src.schemas.health_schemas import LivenessResponse, HealthStatus, HealthResponse
from src.utils.logging_decorator import log

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    response_model=LivenessResponse,
    summary="Liveness probe: проверка, что процесс приложения запущен"
)
async def liveness_probe():
    return LivenessResponse(
        status=HealthStatus.OK,
        service="reports-api",
    )


@router.get(
    "/db_ready",
    status_code=status.HTTP_200_OK,
    response_model=HealthResponse,
    summary="Проверка готовности базы данных"
)
@log("db_readiness_probe")
async def db_readiness_probe():
    db_ok = await HealthDB.check_database()
    response = HealthResponse(
        status=HealthStatus.OK if db_ok else HealthStatus.ERROR,
        checks={"database": "connected" if db_ok else "failed"}
    )
    if not db_ok:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=response.model_dump())
    return response
