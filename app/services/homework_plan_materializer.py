import logging
import uuid
from datetime import date, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.crud.homework_plan import _lock_plan

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
    plan = _lock_plan(db, plan_id)
    if (
        plan is None
        or plan.family_id != family_id
        or plan.is_deleted
        or plan.start_date > through_date
    ):
        return None
    # The row lock protects the relationship while the current transaction runs.
    # Loading after locking ensures a competing edit has committed its final template.
    plan.dictation_items
    return plan


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


def _same_materialization_keys_exist(
    session_factory,
    plan_id: uuid.UUID,
    family_id: uuid.UUID,
    through_date: date,
) -> bool:
    with session_factory() as db:
        plan = (
            db.query(HomeworkPlan)
            .filter(HomeworkPlan.id == plan_id, HomeworkPlan.family_id == family_id)
            .one_or_none()
        )
        if plan is None:
            return False
        target_dates = date_range(plan.start_date, min(plan.end_date, through_date))
        if not target_dates:
            return True
        existing_count = (
            db.query(Task.id)
            .filter(Task.source_plan_id == plan_id, Task.date.in_(target_dates))
            .count()
        )
        return existing_count == len(target_dates)


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
        except IntegrityError:
            if _same_materialization_keys_exist(
                session_factory, plan_id, family_id, through_date
            ):
                results.append(PlanMaterializeResult.success(plan_id, []))
            else:
                logger.exception(
                    "plan materialization integrity conflict",
                    extra={"plan_id": str(plan_id)},
                )
                results.append(PlanMaterializeResult.failed(plan_id, "materialization_failed"))
        except Exception:
            logger.exception("plan materialization failed", extra={"plan_id": str(plan_id)})
            results.append(PlanMaterializeResult.failed(plan_id, "materialization_failed"))
    return MaterializeResult.from_plans(results)
