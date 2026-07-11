import uuid
from datetime import date, datetime, timedelta
from typing import Literal, Self

from pydantic import BaseModel, Field, field_validator, model_validator

from app.core.config import settings
from app.models.task import TaskType
from app.schemas.dictation_item import DictationItemCreate

PlanRangeType = Literal["week", "month", "custom"]
PlanStatus = Literal["upcoming", "active"]
MaterializePlanStatus = Literal["success", "failed"]
MaterializeErrorCode = Literal["materialization_failed", "plan_changed", "plan_unavailable"]


class _PlanFields(BaseModel):
    type: TaskType
    title: str
    desc: str | None
    duration: int | None
    subject: str | None
    dictation_items: list[DictationItemCreate]

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("title must not be blank")
        return value

    @field_validator("duration")
    @classmethod
    def validate_duration(cls, value: int | None) -> int | None:
        if value is not None and value <= 0:
            raise ValueError("duration must be greater than zero")
        return value

    @field_validator("dictation_items")
    @classmethod
    def normalize_dictation_items(cls, items: list[DictationItemCreate]) -> list[DictationItemCreate]:
        normalized: list[DictationItemCreate] = []
        seen: set[str] = set()
        for item in items:
            content = item.content.strip()
            if not content:
                raise ValueError("dictation item content must not be blank")
            key = content.casefold()
            if key in seen:
                raise ValueError("dictation item content must be unique")
            seen.add(key)
            normalized.append(item.model_copy(update={"content": content}))
        return normalized


class HomeworkPlanCreate(_PlanFields):
    desc: str | None = None
    duration: int | None = None
    subject: str | None = None
    range_type: PlanRangeType
    start_date: date | None = None
    end_date: date | None = None
    dictation_items: list[DictationItemCreate] = Field(default_factory=list)

    def resolve_dates(self, today: date) -> tuple[date, date]:
        if self.range_type == "week":
            return today, today + timedelta(days=6)
        if self.range_type == "month":
            return today, today + timedelta(days=29)
        if self.start_date is None or self.end_date is None:
            raise ValueError("custom range requires start_date and end_date")
        if self.start_date < today:
            raise ValueError("start_date must not be before today")
        if self.end_date < self.start_date:
            raise ValueError("end_date must not be before start_date")
        if (self.end_date - self.start_date).days + 1 > settings.MAX_HOMEWORK_PLAN_DAYS:
            raise ValueError("date range exceeds configured maximum")
        return self.start_date, self.end_date


class HomeworkPlanUpdate(_PlanFields):
    start_date: date
    end_date: date
    updated_at: datetime

    @model_validator(mode="after")
    def validate_dates(self) -> Self:
        if self.end_date < self.start_date:
            raise ValueError("end_date must not be before start_date")
        if (self.end_date - self.start_date).days + 1 > settings.MAX_HOMEWORK_PLAN_DAYS:
            raise ValueError("date range exceeds configured maximum")
        return self


class HomeworkPlanOut(BaseModel):
    id: uuid.UUID
    type: TaskType
    title: str
    desc: str | None = None
    duration: int | None = None
    subject: str | None = None
    start_date: date
    end_date: date
    status: PlanStatus
    has_dictation: bool
    dictation_count: int
    total_days: int
    generated_count: int
    remaining_days: int | None = None
    days_until_start: int | None = None
    today_generated: bool
    updated_at: datetime

    model_config = {"from_attributes": True}


class HomeworkPlanDetailOut(HomeworkPlanOut):
    dictation_items: list[DictationItemCreate] = Field(default_factory=list)


class PlanMaterializeResult(BaseModel):
    plan_id: uuid.UUID
    created_dates: list[date] = Field(default_factory=list)
    status: MaterializePlanStatus
    error: MaterializeErrorCode | None = None

    @classmethod
    def success(cls, plan_id: uuid.UUID, created_dates: list[date]) -> "PlanMaterializeResult":
        return cls(plan_id=plan_id, created_dates=created_dates, status="success")

    @classmethod
    def failed(cls, plan_id: uuid.UUID, error: MaterializeErrorCode) -> "PlanMaterializeResult":
        return cls(plan_id=plan_id, status="failed", error=error)


class MaterializeResult(BaseModel):
    created_count: int
    success_count: int
    failed_count: int
    plans: list[PlanMaterializeResult]

    @classmethod
    def from_plans(cls, plans: list[PlanMaterializeResult]) -> "MaterializeResult":
        return cls(
            created_count=sum(len(plan.created_dates) for plan in plans),
            success_count=sum(plan.status == "success" for plan in plans),
            failed_count=sum(plan.status == "failed" for plan in plans),
            plans=plans,
        )
