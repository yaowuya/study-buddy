import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.db_types import GUID
from app.models.task import TaskType


class HomeworkPlan(Base):
    __tablename__ = "homework_plans"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("families.id"), nullable=False, index=True)
    created_by: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id"), nullable=False)
    type: Mapped[TaskType] = mapped_column(String(10), nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    desc: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration: Mapped[int | None] = mapped_column(Integer, nullable=True)
    subject: Mapped[str | None] = mapped_column(String(20), nullable=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    dictation_items: Mapped[list["HomeworkPlanDictationItem"]] = relationship(
        back_populates="plan",
        cascade="all, delete-orphan",
        order_by="HomeworkPlanDictationItem.position",
    )
    tasks: Mapped[list["Task"]] = relationship(back_populates="source_plan")


class HomeworkPlanDictationItem(Base):
    __tablename__ = "homework_plan_dictation_items"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    plan_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("homework_plans.id"), nullable=False, index=True
    )
    content: Mapped[str] = mapped_column(String(200), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)

    plan: Mapped["HomeworkPlan"] = relationship(back_populates="dictation_items")
