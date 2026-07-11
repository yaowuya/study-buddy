import logging
import uuid
from datetime import date, timedelta

from sqlalchemy.orm import Session, selectinload

from app.models.dictation_item import DictationItem
from app.models.homework_plan import HomeworkPlan
from app.models.task import Task
from app.schemas.homework_plan import MaterializeResult, PlanMaterializeResult

logger = logging.getLogger(__name__)


def date_range(start: date, end: date) -> list[date]:
    if end < start:
        return []
    return [start + timedelta(days=offset) for offset in range((end - start).days + 1)]


def _candidate_plan_ids(session_factory, family_id: uuid.UUID, through_date: date) -> list[uuid.UUID]:
    with session_factory() as db:
        return [
            plan_id
            for (plan_id,) in (
                db.query(HomeworkPlan.id)
                .filter(
                    HomeworkPlan.family_id == family_id,
                    HomeworkPlan.is_deleted.is_(False),
                    HomeworkPlan.start_date <= through_date,
                )
                .order_by(HomeworkPlan.start_date, HomeworkPlan.created_at, HomeworkPlan.id)
                .all()
            )
        ]


def _lock_and_revalidate(
    db: Session,
    plan_id: uuid.UUID,
    family_id: uuid.UUID,
    through_date: date,
) -> HomeworkPlan | None:
    return (
        db.query(HomeworkPlan)
        .options(selectinload(HomeworkPlan.dictation_items))
        .filter(
            HomeworkPlan.id == plan_id,
            HomeworkPlan.family_id == family_id,
            HomeworkPlan.is_deleted.is_(False),
            HomeworkPlan.start_date <= through_date,
        )
        .with_for_update()
        .one_or_none()
    )


def _create_missing_snapshots(db: Session, plan: HomeworkPlan, through_date: date) -> list[date]:
    end = min(plan.end_date, through_date)
    target_dates = date_range(plan.start_date, end)
    if not target_dates:
        return []
    existing_dates = {
        task_date
        for (task_date,) in (
            db.query(Task.date)
            .filter(Task.source_plan_id == plan.id, Task.date.in_(target_dates))
            .all()
        )
    }
    created_dates = [target_date for target_date in target_dates if target_date not in existing_dates]
    for target_date in created_dates:
        task = Task(
            family_id=plan.family_id,
            type=plan.type,
            title=plan.title,
            desc=plan.desc,
            duration=plan.duration,
            subject=plan.subject,
            date=target_date,
            source_plan_id=plan.id,
        )
        task.dictation_items = [
            DictationItem(content=item.content)
            for item in sorted(plan.dictation_items, key=lambda item: item.position)
        ]
        db.add(task)
    return created_dates


def materialize_family_plans(session_factory, family_id: uuid.UUID, through_date: date) -> MaterializeResult:
    results: list[PlanMaterializeResult] = []
    for plan_id in _candidate_plan_ids(session_factory, family_id, through_date):
        try:
            with session_factory.begin() as db:
                plan = _lock_and_revalidate(db, plan_id, family_id, through_date)
                if plan is None:
                    results.append(PlanMaterializeResult.failed(plan_id, "plan_unavailable"))
                    continue
                created_dates = _create_missing_snapshots(db, plan, through_date)
            results.append(PlanMaterializeResult.success(plan_id, created_dates))
        except Exception:
            logger.exception("plan materialization failed", extra={"plan_id": str(plan_id)})
            results.append(PlanMaterializeResult.failed(plan_id, "materialization_failed"))
    return MaterializeResult.from_plans(results)
