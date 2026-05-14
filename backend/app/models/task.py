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
    __tablename__ = "tasks"  # 任务表

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)  # 任务ID
    family_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("families.id"), nullable=False, index=True)  # 所属家庭ID
    type: Mapped[TaskType] = mapped_column(String(10), nullable=False)  # 任务类型：school=学校作业，home=家庭任务
    title: Mapped[str] = mapped_column(String(100), nullable=False)  # 任务标题
    desc: Mapped[str | None] = mapped_column(Text, nullable=True)  # 任务描述/说明
    duration: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 预计完成时长（分钟）
    status: Mapped[TaskStatus] = mapped_column(String(20), default=TaskStatus.PENDING, nullable=False)  # 任务状态
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)  # 任务日期
    subject: Mapped[str | None] = mapped_column(String(20), nullable=True)  # 科目（如：语文、数学）

    dictation_items: Mapped[list["DictationItem"]] = relationship(back_populates="task", cascade="all, delete-orphan")
    submission: Mapped["Submission | None"] = relationship(back_populates="task", uselist=False)
