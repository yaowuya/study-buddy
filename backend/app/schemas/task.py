import uuid
from datetime import date as DateType

from pydantic import BaseModel

from app.models.task import TaskType, TaskStatus


class TaskCreate(BaseModel):
    type: TaskType
    title: str
    desc: str | None = None
    duration: int | None = None
    date: DateType
    subject: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    desc: str | None = None
    duration: int | None = None
    date: DateType | None = None
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
    date: DateType
    subject: str | None = None
    has_dictation: bool = False

    model_config = {"from_attributes": True}
