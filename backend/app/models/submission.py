import uuid
from datetime import datetime

from sqlalchemy import String, ForeignKey, Text, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Submission(Base):
    __tablename__ = "submissions"  # 作业提交记录表

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)  # 提交记录ID
    task_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tasks.id"), unique=True, nullable=False, index=True)  # 对应任务ID（一任务一提交）
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)  # 家长批改留言
    is_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)  # 批改结果：True=正确，False=需订正，None=未批改
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)  # 学生提交时间

    task: Mapped["Task"] = relationship(back_populates="submission")
