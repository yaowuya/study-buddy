import uuid

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Family(Base):
    __tablename__ = "families"  # 家庭表

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)  # 家庭ID
    code: Mapped[str] = mapped_column(String(6), unique=True, index=True, nullable=False)  # 6位邀请码，家庭成员凭此加入

    members: Mapped[list["User"]] = relationship(back_populates="family")
