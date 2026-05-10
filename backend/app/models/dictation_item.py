import uuid

from sqlalchemy import String, ForeignKey, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DictationItem(Base):
    __tablename__ = "dictation_items"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tasks.id"), nullable=False, index=True)
    content: Mapped[str] = mapped_column(String(200), nullable=False)
    speed: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    pause_interval: Mapped[int] = mapped_column(Integer, default=3, nullable=False)

    task: Mapped["Task"] = relationship(back_populates="dictation_items")
