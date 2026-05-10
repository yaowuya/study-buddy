import uuid

from pydantic import BaseModel


class FamilyBind(BaseModel):
    code: str


class FamilyOut(BaseModel):
    id: uuid.UUID
    code: str

    model_config = {"from_attributes": True}
