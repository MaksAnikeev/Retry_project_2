import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index, Integer, String, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column

from src.models import Base


class DeliveryORM(Base):
    __tablename__ = "deliveries"  # ← Исправлено

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        nullable=False,
        index=True,
    )
    product_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )
    price: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="processing",
        server_default="processing",
        nullable=False,
        comment="Статус доставки: processing, delivery, completed, failed",
    )
    driver_id: Mapped[int | None] = mapped_column(
        Uuid,
        nullable=True,
        comment="ID водителя (случайное число)",
    )
    event_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        nullable=False,
        unique=True,
        index=True,
    )
    address: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )
    delivery_to: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    __table_args__ = (
        Index("ix_deliveries_event_id", "event_id", unique=True),
        Index("ix_deliveries_status_created_at", "status", "created_at"),
    )
