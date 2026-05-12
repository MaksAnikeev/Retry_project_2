from src.models import OverdueTasksORM
from src.repositories.mappers.base_mapp import DataMapper
from src.schemas.over_tasks_schemas import TaskCreateSchemas


class TaskDataMapper(DataMapper):
    db_model = OverdueTasksORM
    schemas = TaskCreateSchemas
