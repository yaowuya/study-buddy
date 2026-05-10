import uuid
from datetime import datetime

from pydantic import BaseModel


class SubmissionCreate(BaseModel):
    task_id: uuid.UUID


class SubmissionGrade(BaseModel):
    is_correct: bool
    comment: str | None = None


class SubmissionOut(BaseModel):
    id: uuid.UUID
    task_id: uuid.UUID
    comment: str | None = None
    is_correct: bool | None = None
    submitted_at: datetime

    model_config = {"from_attributes": True}
