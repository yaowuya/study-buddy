import uuid

from sqlalchemy import String, ForeignKey, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db_types import GUID
from app.database import Base


class DictationItem(Base):
    __tablename__ = "dictation_items"  # 听写条目表

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)  # 听写条目ID
    task_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("tasks.id"), nullable=False, index=True)  # 所属任务ID
    content: Mapped[str] = mapped_column(String(200), nullable=False)  # 听写内容（词语或句子）
    speed: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)  # TTS语速，1.0为正常速度
    pause_interval: Mapped[int] = mapped_column(Integer, default=3, nullable=False)  # 每条朗读后暂停秒数

    task: Mapped["Task"] = relationship(back_populates="dictation_items")
