from src.models.reports import ReportsORM
from src.repositories.base import BaseRepository
from src.schemas.reports_schemas import ReportGetSchemas


class ReportRepository(BaseRepository):
    model = ReportsORM
    schemas = ReportGetSchemas
