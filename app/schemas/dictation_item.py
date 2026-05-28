import uuid

from pydantic import BaseModel


class DictationItemCreate(BaseModel):
    content: str
    speed: float = 1.0
    pause_interval: int = 3


class DictationItemBatch(BaseModel):
    task_id: uuid.UUID
    items: list[DictationItemCreate]


class DictationItemOut(BaseModel):
    id: uuid.UUID
    task_id: uuid.UUID
    content: str
    speed: float
    pause_interval: int

    model_config = {"from_attributes": True}
