import uuid

from sqlalchemy import String, UUID, Float
from sqlalchemy.orm import Mapped, mapped_column

from src.models import Base


class ReportsORM(Base):
    __tablename__ = "reports"

    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        unique=True,
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    complexity: Mapped[str] = mapped_column(String(50), nullable=False)
    estimated_hours: Mapped[float] = mapped_column(Float, nullable=False)
    priority: Mapped[str] = mapped_column(String(50), nullable=False)
