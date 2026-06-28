from fastapi import APIRouter, status
from starlette.responses import JSONResponse

from src.api.routers.health.utils import HealthDB
from src.schemas.health_schemas import LivenessResponse, HealthStatus, ReadinessResponse, ComponentStatus

router = APIRouter(tags=["Health"])

@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    response_model=LivenessResponse,
    summary="Liveness probe"
)
async def liveness_probe():
    return LivenessResponse(
        status=HealthStatus.OK,
        service="tasks-api",
    )


@router.get(
    "/ready",
    status_code=status.HTTP_200_OK,
    response_model=ReadinessResponse,
    summary="Readiness probe"
)
async def readiness_probe():
    db_ok = await HealthDB.check_database()

    db_status = HealthStatus.OK if db_ok else HealthStatus.ERROR
    db_status_info = ComponentStatus(
        name="database",
        status=db_status,
        message=None if db_ok else "Database connection failed",
    )
    response = ReadinessResponse(
        status=db_status,
        service="tasks-api",
        components=[db_status_info],
    )

    if not db_ok:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=response.model_dump(),
        )

    return response