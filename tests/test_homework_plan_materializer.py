from datetime import date

import pytest

from app.database import Base
from app.models.family import Family
from app.models.homework_plan import HomeworkPlan, HomeworkPlanDictationItem
from app.models.task import Task
from app.models.user import User, UserRole
from app.services.homework_plan_materializer import date_range, materialize_family_plans
from tests.conftest import TestSessionLocal, engine


@pytest.fixture(autouse=True)
def clean_data():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


def create_plan(*, family_id, parent_id, start, end, title="每日听写", words=("甲", "乙")):
    with TestSessionLocal.begin() as db:
        plan = HomeworkPlan(
            family_id=family_id,
            created_by=parent_id,
            type="home",
            title=title,
            desc="模板说明",
            duration=15,
            subject="语文",
            start_date=start,
            end_date=end,
        )
        plan.dictation_items = [
            HomeworkPlanDictationItem(content=word, position=position)
            for position, word in enumerate(words)
        ]
        db.add(plan)
        db.flush()
        return plan.id


@pytest.fixture
def family_parent():
    with TestSessionLocal.begin() as db:
        family = Family(code="200001")
        db.add(family)
        db.flush()
        parent = User(
            role=UserRole.PARENT,
            phone="13100000001",
            hashed_password="hash",
            family_id=family.id,
        )
        db.add(parent)
        db.flush()
        return family.id, parent.id


def test_date_range_handles_leap_day_and_empty_range():
    assert date_range(date(2024, 2, 28), date(2024, 3, 1)) == [
        date(2024, 2, 28),
        date(2024, 2, 29),
        date(2024, 3, 1),
    ]
    assert date_range(date(2026, 7, 12), date(2026, 7, 11)) == []


def test_backfills_missing_dates_idempotently(family_parent):
    family_id, parent_id = family_parent
    plan_id = create_plan(
        family_id=family_id,
        parent_id=parent_id,
        start=date(2026, 7, 11),
        end=date(2026, 7, 13),
    )

    first = materialize_family_plans(TestSessionLocal, family_id, date(2026, 7, 13))
    second = materialize_family_plans(TestSessionLocal, family_id, date(2026, 7, 13))

    assert first.created_count == 3
    assert second.created_count == 0
    with TestSessionLocal() as db:
        tasks = db.query(Task).filter(Task.source_plan_id == plan_id).order_by(Task.date).all()
        assert [task.date for task in tasks] == [
            date(2026, 7, 11),
            date(2026, 7, 12),
            date(2026, 7, 13),
        ]
        assert [[item.content for item in task.dictation_items] for task in tasks] == [["甲", "乙"]] * 3
        assert all(task.title == "每日听写" and task.desc == "模板说明" for task in tasks)


def test_expired_candidates_are_backfilled_and_failures_are_isolated(family_parent, monkeypatch):
    family_id, parent_id = family_parent
    valid_id = create_plan(
        family_id=family_id,
        parent_id=parent_id,
        start=date(2026, 7, 9),
        end=date(2026, 7, 10),
        words=(),
    )
    broken_id = create_plan(
        family_id=family_id,
        parent_id=parent_id,
        start=date(2026, 7, 10),
        end=date(2026, 7, 10),
        title="失败模板",
        words=(),
    )
    from app.services import homework_plan_materializer as materializer

    original_create = materializer._create_missing_snapshots

    def fail_one_plan(db, plan, through_date):
        if plan.id == broken_id:
            raise RuntimeError("sensitive database detail")
        return original_create(db, plan, through_date)

    monkeypatch.setattr(materializer, "_create_missing_snapshots", fail_one_plan)

    result = materialize_family_plans(TestSessionLocal, family_id, date(2026, 7, 11))

    assert result.created_count == 2
    assert result.success_count == 1
    assert result.failed_count == 1
    assert [(plan.plan_id, plan.status, plan.error) for plan in result.plans] == [
        (valid_id, "success", None),
        (broken_id, "failed", "materialization_failed"),
    ]
    with TestSessionLocal() as db:
        assert db.query(Task).filter(Task.source_plan_id == valid_id).count() == 2
        assert db.query(Task).filter(Task.source_plan_id == broken_id).count() == 0
