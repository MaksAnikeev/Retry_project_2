from typing import List

from fastapi import APIRouter

from src.api.dependencies import DBDep, TaskClientDep
from src.exceptions import (
    TooLongParameterException,
    UserNotFoundHTTPException,
    UserNotFoundException,
    TaskNotFoundException,
    TaskNotFoundHTTPException,
    TooLongParameterHTTPException,
    ObjectNotFoundException,
    UserTaskNotFoundHTTPException,
)

from src.schemas.over_tasks_schemas import TaskCreateSchemas
from src.services.task_service import TaskService

router = APIRouter(prefix="/over_tasks", tags=["Просроченные задачи"])


@router.get("/", summary="Получить все просроченные задачи пользователя")
async def get_over_tasks(
    user_id: int,
    db: DBDep):
    try:
        over_tasks = await TaskService(db).get_all_with_parameters(user_id=user_id)
    except UserNotFoundException:
        raise UserNotFoundHTTPException

    return {"status": "success", "tasks": over_tasks, "details": None}


@router.get("/new_tasks", summary="Посмотреть новообразовавшиеся просроченные задачи на текущую дату")
async def get_over_tasks(
    user_id: int,
    http_client: TaskClientDep,
    db: DBDep
):
    try:
        tasks: List[TaskCreateSchemas] = await TaskService(db=db, http_client=http_client).get_overdue_tasks(user_id=user_id)
    except UserNotFoundException:
        raise UserNotFoundHTTPException
    return {
        "status": "OK",
        "description": f"Количество просроченных задач {len(tasks)}.",
        "task_info": tasks,
    }


@router.get("/{task_id}", summary="Получить данные по просроченной задаче")
async def get_task(
    user_id: int,
    task_id: int,
    db: DBDep,
):
    try:
        over_task = await TaskService(db).get_one(
            user_id=user_id,
            task_id=task_id,
        )
    except TaskNotFoundException:
        raise TaskNotFoundHTTPException
    except ObjectNotFoundException:
        raise UserTaskNotFoundHTTPException

    return {"status": "success", "task": over_task, "detail": None}


@router.post("/", summary="Добавить новообразовавшиеся просроченные задачи на текущую дату")
async def add_over_task(
    user_id: int,
    http_client: TaskClientDep,
    db: DBDep,
):
    try:
        tasks: List[TaskCreateSchemas] = await TaskService(db=db, http_client=http_client).add_overdue_tasks(user_id=user_id)
    except UserNotFoundException:
        await db.rollback()
        raise UserNotFoundHTTPException
    except TaskNotFoundException:
        await db.rollback()
        raise TaskNotFoundHTTPException
    except Exception:
        await db.rollback()
        raise
    return {
        "status": "OK",
        "description": f"{len(tasks)} просроченных задач успешно добавлен пользователю с ид {user_id}.",
        "task_info": f"Названия просроченных задач {[task.title for task in tasks]}",
    }


@router.delete("/{task_id}", summary="Удалить просроченную задачу по ИД")
async def del_over_task(
    user_id: int,
    task_id: int,
    db: DBDep,
):
    try:
        task = await TaskService(db).delete(user_id=user_id, task_id=task_id)
    except UserNotFoundException:
        raise UserNotFoundHTTPException
    except TaskNotFoundException:
        raise TaskNotFoundHTTPException
    except TooLongParameterException:
        raise TooLongParameterHTTPException
    except ObjectNotFoundException:
        raise UserTaskNotFoundHTTPException

    await db.commit()
    return {
        "status": "OK",
        "description": f"Задача с ид {task.id} удалена.",
        "delete_task_info": task,
    }