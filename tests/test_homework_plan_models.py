import uuid
from datetime import date

from sqlalchemy import UniqueConstraint

from app.core.config import settings
from app.models import HomeworkPlan, HomeworkPlanDictationItem, Task, TaskType


def test_plan_models_and_task_source_constraints():
    plan = HomeworkPlan(
        family_id=uuid.uuid4(),
        created_by=uuid.uuid4(),
        type=TaskType.HOME,
        title="每日听写",
        start_date=date(2026, 7, 11),
        end_date=date(2026, 7, 17),
    )

    assert HomeworkPlan.__table__.c.is_deleted.default.arg is False
    assert HomeworkPlan.__table__.c.is_deleted.server_default is not None
    assert settings.BUSINESS_TIMEZONE == "Asia/Shanghai"
    assert settings.MAX_HOMEWORK_PLAN_DAYS == 366
    assert Task.__table__.c.source_plan_id.nullable
    assert any(
        isinstance(constraint, UniqueConstraint)
        and constraint.name == "uq_tasks_source_plan_date"
        and set(constraint.columns.keys()) == {"source_plan_id", "date"}
        for constraint in Task.__table__.constraints
    )


def test_plan_dictation_items_are_ordered_without_task_delete_cascade():
    assert HomeworkPlan.dictation_items.property.order_by
    assert "delete-orphan" in HomeworkPlan.dictation_items.property.cascade
    assert "delete" not in HomeworkPlan.tasks.property.cascade
    assert HomeworkPlanDictationItem.__table__.c.position.nullable is False
