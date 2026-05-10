import uuid
from datetime import date
from enum import StrEnum

from sqlalchemy import String, Date, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TaskType(StrEnum):
    SCHOOL = "school"
    HOME = "home"


class TaskStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    GRADED = "graded"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("families.id"), nullable=False, index=True)
    type: Mapped[TaskType] = mapped_column(String(10), nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    desc: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(String(20), default=TaskStatus.PENDING, nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    subject: Mapped[str | None] = mapped_column(String(20), nullable=True)

    dictation_items: Mapped[list["DictationItem"]] = relationship(back_populates="task", cascade="all, delete-orphan")
    submission: Mapped["Submission | None"] = relationship(back_populates="task", uselist=False)
