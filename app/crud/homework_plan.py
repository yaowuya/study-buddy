import uuid
from dataclasses import dataclass
from datetime import date, datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.models.homework_plan import HomeworkPlan, HomeworkPlanDictationItem
from app.models.task import Task
from app.schemas.homework_plan import HomeworkPlanCreate, HomeworkPlanUpdate


class PlanVersionConflict(Exception):
    """The supplied optimistic concurrency token is stale."""


class PlanDateConflict(Exception):
    """The requested update violates lifecycle date rules."""


@dataclass(frozen=True)
class ActivePlanRow:
    plan: HomeworkPlan
    generated_count: int


def _replace_dictation_items(plan: HomeworkPlan, items) -> None:
    plan.dictation_items = [
        HomeworkPlanDictationItem(content=item.content.strip(), position=position)
        for position, item in enumerate(items)
    ]


def create_plan(
    db: Session,
    family_id: uuid.UUID,
    created_by: uuid.UUID,
    command: HomeworkPlanCreate,
) -> HomeworkPlan:
    start_date, end_date = command.resolve_dates(date.today())
    plan = HomeworkPlan(
        family_id=family_id,
        created_by=created_by,
        type=command.type,
        title=command.title,
        desc=command.desc,
        duration=command.duration,
        subject=command.subject,
        start_date=start_date,
        end_date=end_date,
    )
    _replace_dictation_items(plan, command.dictation_items)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def get_active_plans(db: Session, family_id: uuid.UUID, today: date) -> list[ActivePlanRow]:
    generated = (
        db.query(
            Task.source_plan_id.label("plan_id"),
            func.count(Task.id).label("generated_count"),
        )
        .filter(Task.source_plan_id.is_not(None))
        .group_by(Task.source_plan_id)
        .subquery()
    )
    rows = (
        db.query(HomeworkPlan, func.coalesce(generated.c.generated_count, 0))
        .outerjoin(generated, generated.c.plan_id == HomeworkPlan.id)
        .options(selectinload(HomeworkPlan.dictation_items))
        .filter(
            HomeworkPlan.family_id == family_id,
            HomeworkPlan.is_deleted.is_(False),
            HomeworkPlan.end_date >= today,
        )
        .order_by(HomeworkPlan.start_date, HomeworkPlan.created_at, HomeworkPlan.id)
        .all()
    )
    return [ActivePlanRow(plan=plan, generated_count=int(count)) for plan, count in rows]


def get_plan_for_family(
    db: Session,
    plan_id: uuid.UUID,
    family_id: uuid.UUID,
    *,
    include_deleted: bool = False,
) -> HomeworkPlan | None:
    query = db.query(HomeworkPlan).options(selectinload(HomeworkPlan.dictation_items)).filter(
        HomeworkPlan.id == plan_id,
        HomeworkPlan.family_id == family_id,
    )
    if not include_deleted:
        query = query.filter(HomeworkPlan.is_deleted.is_(False))
    return query.one_or_none()


def _tokens_equal(actual: datetime, supplied: datetime) -> bool:
    if actual.tzinfo is None and supplied.tzinfo is not None:
        supplied = supplied.astimezone(timezone.utc).replace(tzinfo=None)
    elif actual.tzinfo is not None and supplied.tzinfo is None:
        actual = actual.astimezone(timezone.utc).replace(tzinfo=None)
    return actual == supplied


def _lock_plan(db: Session, plan_id: uuid.UUID) -> HomeworkPlan | None:
    return (
        db.query(HomeworkPlan)
        .filter(HomeworkPlan.id == plan_id)
        .with_for_update()
        .one_or_none()
    )


def update_plan(
    db: Session,
    plan_id: uuid.UUID,
    family_id: uuid.UUID,
    command: HomeworkPlanUpdate,
    today: date,
) -> HomeworkPlan | None:
    plan = _lock_plan(db, plan_id)
    if plan is None or plan.family_id != family_id or plan.is_deleted:
        return None
    if not _tokens_equal(plan.updated_at, command.updated_at):
        raise PlanVersionConflict
    if plan.start_date <= today and command.start_date != plan.start_date:
        raise PlanDateConflict("started plan start_date is immutable")
    if command.end_date < today:
        raise PlanDateConflict("end_date must not be before today")

    for field in ("type", "title", "desc", "duration", "subject", "start_date", "end_date"):
        setattr(plan, field, getattr(command, field))
    _replace_dictation_items(plan, command.dictation_items)
    plan.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(plan)
    return plan


def soft_delete_plan(
    db: Session,
    plan_id: uuid.UUID,
    family_id: uuid.UUID,
) -> HomeworkPlan | None:
    plan = _lock_plan(db, plan_id)
    if plan is None or plan.family_id != family_id:
        return None
    if not plan.is_deleted:
        plan.is_deleted = True
        plan.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(plan)
    return plan
