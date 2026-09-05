import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class DiseaseReport(Base):
    __tablename__ = "disease_reports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    animal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("animals.id"),
        nullable=False,
        index=True,
    )

    reported_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    symptoms: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    temperature: Mapped[float | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )

    image_path: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    latitude: Mapped[float | None] = mapped_column(
        Numeric(9, 6),
        nullable=True,
    )

    longitude: Mapped[float | None] = mapped_column(
        Numeric(9, 6),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="PENDING_AI",
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        index=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )