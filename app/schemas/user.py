import uuid

from pydantic import BaseModel

from app.models.user import UserRole


class UserRegister(BaseModel):
    phone: str
    password: str
    role: UserRole


class UserLogin(BaseModel):
    phone: str
    password: str


class UserOut(BaseModel):
    id: uuid.UUID
    phone: str
    role: UserRole
    family_id: uuid.UUID | None = None

    model_config = {"from_attributes": True}
