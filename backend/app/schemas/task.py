import uuid
from datetime import date

from pydantic import BaseModel

from app.models.task import TaskType, TaskStatus


class TaskCreate(BaseModel):
    type: TaskType
    title: str
    desc: str | None = None
    duration: int | None = None
    date: date
    subject: str | None = None


class TaskUpdateStatus(BaseModel):
    status: TaskStatus


class TaskOut(BaseModel):
    id: uuid.UUID
    type: TaskType
    title: str
    desc: str | None = None
    duration: int | None = None
    status: TaskStatus
    date: date
    subject: str | None = None

    model_config = {"from_attributes": True}
