import uuid

from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db_types import GUID
from app.database import Base


class Family(Base):
    __tablename__ = "families"  # 家庭表

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)  # 家庭ID
    code: Mapped[str] = mapped_column(String(6), unique=True, index=True, nullable=False)  # 6位邀请码，家庭成员凭此加入
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # 软删除标记

    members: Mapped[list["User"]] = relationship(back_populates="family")
