import uuid
from enum import StrEnum

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserRole(StrEnum):
    PARENT = "parent"
    STUDENT = "student"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    role: Mapped[UserRole] = mapped_column(String(10), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(128), nullable=False)
    family_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("families.id"), nullable=True)

    family: Mapped["Family | None"] = relationship(back_populates="members")
