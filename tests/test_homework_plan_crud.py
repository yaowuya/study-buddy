from datetime import date, datetime, timezone
from types import SimpleNamespace

import pytest

from app.crud.homework_plan import (
    PlanVersionConflict,
    create_plan,
    get_active_plans,
    get_plan_for_family,
    soft_delete_plan,
    update_plan,
)
from app.database import Base
from app.models.family import Family
from app.models.homework_plan import HomeworkPlan
from app.models.task import Task
from app.models.user import User, UserRole
from app.schemas.dictation_item import DictationItemCreate
from app.schemas.homework_plan import HomeworkPlanCreate, HomeworkPlanUpdate
from tests.conftest import TestSessionLocal, engine


@pytest.fixture(autouse=True)
def clean_plan_data():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def db():
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


def make_family_parent(db, code: str, phone: str):
    family = Family(code=code)
    db.add(family)
    db.flush()
    parent = User(
        role=UserRole.PARENT,
        phone=phone,
        hashed_password="hash",
        family_id=family.id,
    )
    db.add(parent)
    db.commit()
    return family, parent


def plan_command(**overrides):
    values = {
        "type": "home",
        "title": "每日听写",
        "range_type": "custom",
        "start_date": date(2026, 7, 11),
        "end_date": date(2026, 7, 13),
        "dictation_items": [
            DictationItemCreate(content=" 甲 "),
            DictationItemCreate(content="乙"),
        ],
    }
    values.update(overrides)
    return HomeworkPlanCreate(**values)


def update_command(plan, **overrides):
    values = {
        "type": plan.type,
        "title": "更新模板",
        "desc": plan.desc,
        "duration": plan.duration,
        "subject": plan.subject,
        "start_date": plan.start_date,
        "end_date": plan.end_date,
        "updated_at": plan.updated_at,
        "dictation_items": [DictationItemCreate(content="新词")],
    }
    values.update(overrides)
    return HomeworkPlanUpdate(**values)


def test_create_plan_persists_ordered_items(db):
    family, parent = make_family_parent(db, "100001", "13000000001")

    plan = create_plan(db, family.id, parent.id, plan_command(), date(2026, 7, 11))

    assert plan.family_id == family.id
    assert [item.content for item in plan.dictation_items] == ["甲", "乙"]
    assert [item.position for item in plan.dictation_items] == [0, 1]
    assert db.get(HomeworkPlan, plan.id) is not None


def test_active_plans_are_family_scoped_and_aggregated(db):
    family_a, parent_a = make_family_parent(db, "100002", "13000000002")
    family_b, parent_b = make_family_parent(db, "100003", "13000000003")
    today = date(2026, 7, 11)
    mine = create_plan(db, family_a.id, parent_a.id, plan_command(end_date=today), today)
    create_plan(db, family_b.id, parent_b.id, plan_command(end_date=today), today)
    db.add(Task(family_id=family_a.id, source_plan_id=mine.id, date=today, type="home", title="快照"))
    db.commit()

    rows = get_active_plans(db, family_a.id, today)

    assert [(row.plan.id, row.generated_count) for row in rows] == [(mine.id, 1)]


def test_update_and_delete_preserve_generated_snapshot(db):
    family, parent = make_family_parent(db, "100004", "13000000004")
    other, _ = make_family_parent(db, "100005", "13000000005")
    today = date(2026, 7, 11)
    plan = create_plan(db, family.id, parent.id, plan_command(), date(2026, 7, 11))
    snapshot = Task(
        family_id=family.id,
        source_plan_id=plan.id,
        date=today,
        type=plan.type,
        title=plan.title,
        desc=plan.desc,
    )
    db.add(snapshot)
    db.commit()
    snapshot_id = snapshot.id

    assert get_plan_for_family(db, plan.id, other.id) is None
    with pytest.raises(PlanVersionConflict):
        update_plan(
            db,
            plan.id,
            family.id,
            update_command(plan, updated_at=datetime(2000, 1, 1, tzinfo=timezone.utc)),
            today,
        )

    current = get_plan_for_family(db, plan.id, family.id)
    updated = update_plan(db, plan.id, family.id, update_command(current), today)
    assert updated.title == "更新模板"
    assert [item.content for item in updated.dictation_items] == ["新词"]
    assert db.get(Task, snapshot_id).title == "每日听写"

    deleted = soft_delete_plan(db, plan.id, family.id)
    repeated = soft_delete_plan(db, plan.id, family.id)
    assert deleted is repeated
    assert repeated.is_deleted is True
    assert db.get(Task, snapshot_id) is not None
