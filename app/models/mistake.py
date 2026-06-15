import uuid

from sqlalchemy import String, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.db_types import GUID
from app.database import Base


class Mistake(Base):
    __tablename__ = "mistakes"  # 错题记录表

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)  # 错题ID
    task_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("tasks.id"), nullable=False, index=True)  # 来源任务ID
    subject: Mapped[str | None] = mapped_column(String(20), nullable=True)  # 科目（冗余存储，方便按科目筛选）
    archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # 是否已归档（已掌握）
