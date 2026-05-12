from datetime import date

from pydantic import BaseModel, Field

from src.schemas.base_schema import ChangeBaseSchema


class TaskCreateSchemas(BaseModel):
    id: int = Field(..., description="ИД задачи")
    user_id: int = Field(..., description="ИД пользователя")
    title: str = Field(..., description="Короткое название задачи")
    description: str | None = Field(None, description="Описание задачи")
    cause_overdue: str | None = Field(None, description="Причина просрока")
    finish_date: date = Field(..., description="Изначальная дата выполнения задачи")
    new_finish_date: date = Field(..., description="Новая дата выполнения задачи")


class TaskAPIGetSchemas(BaseModel):
    id: int = Field(..., description="ИД задачи")
    user_id: int = Field(..., description="ИД пользователя")
    title: str = Field(..., description="Короткое название задачи")
    description: str | None = Field(None, description="Описание задачи")
    finish_date: date = Field(..., description="Плановая дата выполнения задачи")


class TaskChangeSchemas(ChangeBaseSchema):
    cause_overdue: str | None = Field(None, description="Причина просрока")
    new_finish_date: date | None = Field(None, description="Новая дата выполнения задачи")

example_change_task = {
    "1": {
        "summary": "Задача 1",
        "value": {
            "cause_overdue": "Забыл посмотреть трекер задач",
        },
    },
    "2": {
        "summary": "Задача 2",
        "value": {
            "cause_overdue": "Много было другой работы",
            "new_finish_date": '2026-06-01',
        },
    },
}