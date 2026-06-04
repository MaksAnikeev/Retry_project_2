from fastapi import APIRouter, status
from starlette.responses import JSONResponse

from src.api.routers.health.utils import HealthDB
from src.utils.logging_decorator import log

router = APIRouter(tags=["Health"])


@router.get("/health", status_code=status.HTTP_200_OK)
@log("liveness_probe")
async def liveness_probe():
    return {"status": "ok", "service": "reports-api"}


@router.get("/db_ready", status_code=status.HTTP_200_OK)
@log("db_readiness_probe")
async def db_readiness_probe():
    db_ok = await HealthDB.check_database()

    if not db_ok:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "error",
                "checks": {
                    "database": "failed",
                }
            }
        )

    return {
        "status": "ok",
        "checks": {
            "database": "connected",
        }
    }