import uuid
from enum import StrEnum

from sqlalchemy import String, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db_types import GUID
from app.database import Base


class UserRole(StrEnum):
    PARENT = "parent"
    STUDENT = "student"


class User(Base):
    __tablename__ = "users"  # 用户表

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)  # 用户ID
    role: Mapped[UserRole] = mapped_column(String(10), nullable=False)  # 角色：parent=家长，student=学生
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)  # 手机号（登录账号）
    hashed_password: Mapped[str] = mapped_column(String(128), nullable=False)  # 加密后的密码
    family_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("families.id"), nullable=True)  # 所属家庭ID，未绑定时为空
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)  # 是否启用（禁用后无法登录）
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # 软删除标记

    family: Mapped["Family | None"] = relationship(back_populates="members")
