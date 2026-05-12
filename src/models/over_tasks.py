from datetime import date

from sqlalchemy import String, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db import Base


class OverdueTasksORM(Base):
    __tablename__ = "overdue_tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int]
    title: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str | None]
    cause_overdue: Mapped[str | None]
    finish_date: Mapped[date] = mapped_column(Date(), nullable=False)
    new_finish_date: Mapped[date] = mapped_column(Date(), nullable=False)
