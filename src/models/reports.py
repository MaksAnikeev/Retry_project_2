import uuid

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.models import Base


class ReportsORM(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[uuid.UUID]
    user_id: Mapped[uuid.UUID]
    complexity: Mapped[str] = mapped_column(String(50))
    estimated_hours: Mapped[float]
    priority: Mapped[str] = mapped_column(String(50))
