import uuid
from datetime import date
from typing import Self

from pydantic import BaseModel, Field, model_validator
from enum import Enum


class Complexity(str, Enum):
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class BaseReportSchemas(BaseModel):
    task_id: uuid.UUID = Field(..., description="ИД задачи")
    complexity: Complexity = Field(..., description="Сложность выполняемой задачи")
    estimated_hours: float = Field(..., description="Время на выполнение задачи")
    priority: Priority = Field(..., description="Статус задачи")


class ReportCreateSchemas(BaseReportSchemas):
    user_id: uuid.UUID = Field(..., description="ИД пользователя")


class TaskAPIGetSchemas(BaseModel):
    task_id: uuid.UUID = Field(..., description="ИД задачи")
    user_id: uuid.UUID = Field(..., description="ИД пользователя")
    title: str = Field(..., description="Короткое название задачи")
    description: str | None = Field(None, description="Описание задачи")
    finish_date: date = Field(..., description="Плановая дата выполнения задачи")


class ReportChangeSchemas(BaseModel):
    task_id: uuid.UUID = Field(..., description="ИД задачи")
    complexity: Complexity | None = Field(None, description="Сложность выполняемой задачи")
    estimated_hours: float | None = Field(None, description="Время на выполнение задачи")
    priority: Priority | None = Field(None, description="Статус задачи")

    @model_validator(mode="after")
    def check_unique_task_titles(self) -> Self:
        if not self.tasks:
            return self
        titles = [task.title for task in self.tasks]
        seen: set[str] = set()
        duplicates: list[str] = []
        for title in titles:
            if title in seen and title not in duplicates:
                duplicates.append(title)
            seen.add(title)
        if duplicates:
            raise ValueError(
                f"Duplicate task titles: {duplicates}"
            )
        return self


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


class ReportGetSchemas(BaseReportSchemas):
    pass


class ReportDeletedResponse(BaseModel):
    status: str = Field(default="OK", description="Статус операции")
    description: str = Field(description="Описание результата")
    delete_report_info: ReportGetSchemas = Field(description="Информация по удаленному отчету")