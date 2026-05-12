from src.models import OverdueTasksORM
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import TaskDataMapper


class TasksRepository(BaseRepository):
    model = OverdueTasksORM
    mapper = TaskDataMapper
