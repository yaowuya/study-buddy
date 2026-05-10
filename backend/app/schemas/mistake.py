import uuid

from pydantic import BaseModel


class MistakeOut(BaseModel):
    id: uuid.UUID
    task_id: uuid.UUID
    subject: str | None = None
    archived: bool

    model_config = {"from_attributes": True}
