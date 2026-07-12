import uuid
from datetime import date
from importlib.metadata import version
from zoneinfo import ZoneInfo

from pathlib import Path

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


def test_business_timezone_is_available_in_runtime_environment():
    assert version("tzdata")
    assert ZoneInfo(settings.BUSINESS_TIMEZONE).key == "Asia/Shanghai"


def test_plan_migration_is_storage_safe_and_reversible():
    migration = Path("alembic/versions/d14f8c9a2b61_add_homework_plans.py").read_text(encoding="utf-8")

    assert 'down_revision: Union[str, None] = "c7919be721dd"' in migration
    assert 'sa.Column("source_plan_id", GUID(), nullable=True)' in migration
    assert '"uq_tasks_source_plan_date", "tasks", ["source_plan_id", "date"]' in migration
    assert 'op.drop_column("tasks", "source_plan_id")' in migration
    assert "sa.Uuid()" not in migration


def test_plan_dictation_items_are_ordered_without_task_delete_cascade():
    assert HomeworkPlan.dictation_items.property.order_by
    assert "delete-orphan" in HomeworkPlan.dictation_items.property.cascade
    assert "delete" not in HomeworkPlan.tasks.property.cascade
    assert HomeworkPlanDictationItem.__table__.c.position.nullable is False
