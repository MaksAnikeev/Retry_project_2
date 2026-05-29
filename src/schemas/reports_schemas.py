import uuid
from datetime import date

from pydantic import BaseModel, Field
from enum import Enum

from src.schemas.base_schema import ChangeBaseSchema

class Complexity(str, Enum):
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ReportCreateSchemas(BaseModel):
    task_id: uuid.UUID = Field(..., description="ИД задачи")
    user_id: uuid.UUID = Field(..., description="ИД пользователя")
    complexity: Complexity = Field(..., description="Сложность выполняемой задачи")
    estimated_hours: float = Field(..., description="Время на выполнение задачи")
    priority: Priority = Field(..., description="Статус задачи")


class TaskAPIGetSchemas(BaseModel):
    task_id: uuid.UUID = Field(..., description="ИД задачи")
    user_id: uuid.UUID = Field(..., description="ИД пользователя")
    title: str = Field(..., description="Короткое название задачи")
    description: str | None = Field(None, description="Описание задачи")
    finish_date: date = Field(..., description="Плановая дата выполнения задачи")


class ReportChangeSchemas(ChangeBaseSchema):
    complexity: Complexity | None = Field(None, description="Сложность выполняемой задачи")
    estimated_hours: float | None = Field(None, description="Время на выполнение задачи")
    priority: Priority | None = Field(None, description="Статус задачи")


example_change_task = {
    "1": {
        "summary": "Задача 1",
        "value": {
            "complexity": "hard",
            "estimated_hours": 8
        },
    },
    "2": {
        "summary": "Задача 2",
        "value": {
            "priority": "high",
        },
    },
}

class ReportGetSchemas(BaseModel):
    task_id: uuid.UUID = Field(..., description="ИД задачи")
    complexity: Complexity = Field(..., description="Сложность выполняемой задачи")
    estimated_hours: float = Field(..., description="Время на выполнение задачи")
    priority: Priority = Field(..., description="Статус задачи")