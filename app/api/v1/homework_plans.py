import uuid
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_db, require_parent
from app.crud import homework_plan as plan_crud
from app.database import SessionLocal
from app.models.homework_plan import HomeworkPlan
from app.models.user import User
from app.schemas.dictation_item import DictationItemCreate
from app.schemas.homework_plan import HomeworkPlanCreate, HomeworkPlanDetailOut, HomeworkPlanOut
from app.services.homework_plan_materializer import materialize_family_plans

router = APIRouter(prefix="/homework-plans", tags=["homework-plans"])


def business_today() -> date:
    return datetime.now(ZoneInfo(settings.BUSINESS_TIMEZONE)).date()


def _require_family(user: User) -> None:
    if not user.family_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Not bound to a family")


def _plan_out(plan: HomeworkPlan, today: date, generated_count: int = 0) -> HomeworkPlanOut:
    total_days = (plan.end_date - plan.start_date).days + 1
    upcoming = today < plan.start_date
    return HomeworkPlanOut(
        id=plan.id,
        type=plan.type,
        title=plan.title,
        desc=plan.desc,
        duration=plan.duration,
        subject=plan.subject,
        start_date=plan.start_date,
        end_date=plan.end_date,
        status="upcoming" if upcoming else "active",
        has_dictation=bool(plan.dictation_items),
        dictation_count=len(plan.dictation_items),
        total_days=total_days,
        generated_count=generated_count,
        remaining_days=(plan.end_date - today).days + 1 if not upcoming else None,
        days_until_start=(plan.start_date - today).days if upcoming else None,
        today_generated=any(task.date == today for task in plan.tasks),
        updated_at=plan.updated_at,
    )


def _plan_detail(plan: HomeworkPlan, today: date, generated_count: int = 0) -> HomeworkPlanDetailOut:
    data = _plan_out(plan, today, generated_count).model_dump()
    data["dictation_items"] = [DictationItemCreate(content=item.content) for item in plan.dictation_items]
    return HomeworkPlanDetailOut(**data)


@router.post("/", response_model=HomeworkPlanDetailOut)
def create_homework_plan(
    body: HomeworkPlanCreate,
    user: User = Depends(require_parent),
    db: Session = Depends(get_db),
):
    _require_family(user)
    today = business_today()
    plan = plan_crud.create_plan(db, user.family_id, user.id, body, today)
    if plan.start_date <= today:
        materialize_family_plans(SessionLocal, user.family_id, today)
    refreshed = plan_crud.get_plan_for_family(db, plan.id, user.family_id)
    if refreshed is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Homework plan not found")
    return _plan_detail(refreshed, today, generated_count=len(refreshed.tasks))


@router.get("/", response_model=list[HomeworkPlanOut])
def list_homework_plans(
    user: User = Depends(require_parent),
    db: Session = Depends(get_db),
):
    _require_family(user)
    today = business_today()
    return [_plan_out(row.plan, today, row.generated_count) for row in plan_crud.get_active_plans(db, user.family_id, today)]


@router.get("/{plan_id}", response_model=HomeworkPlanDetailOut)
def get_homework_plan(
    plan_id: uuid.UUID,
    user: User = Depends(require_parent),
    db: Session = Depends(get_db),
):
    _require_family(user)
    plan = plan_crud.get_plan_for_family(db, plan_id, user.family_id)
    if plan is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Homework plan not found")
    return _plan_detail(plan, business_today(), generated_count=len(plan.tasks))
