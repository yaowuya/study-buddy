import os
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.crud.homework_plan import soft_delete_plan, update_plan
from app.models.family import Family
from app.models.homework_plan import HomeworkPlan, HomeworkPlanDictationItem
from app.models.task import Task
from app.models.user import User, UserRole
from app.schemas.homework_plan import HomeworkPlanUpdate
from app.services.homework_plan_materializer import materialize_family_plans

TEST_POSTGRES_URL = os.getenv("TEST_POSTGRES_URL")
pytestmark = pytest.mark.skipif(not TEST_POSTGRES_URL, reason="requires TEST_POSTGRES_URL")


@pytest.fixture
def pg_session_factory():
    engine = create_engine(TEST_POSTGRES_URL)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    yield factory
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def pg_plan(pg_session_factory):
    with pg_session_factory.begin() as db:
        family = Family(code="299901")
        db.add(family)
        db.flush()
        parent = User(
            role=UserRole.PARENT,
            phone="13999990001",
            hashed_password="hash",
            family_id=family.id,
        )
        db.add(parent)
        db.flush()
        plan = HomeworkPlan(
            family_id=family.id,
            created_by=parent.id,
            type="home",
            title="旧模板",
            desc="旧说明",
            duration=10,
            subject="语文",
            start_date=date(2026, 7, 11),
            end_date=date(2026, 7, 11),
        )
        plan.dictation_items = [HomeworkPlanDictationItem(content="旧词", position=0)]
        db.add(plan)
        db.flush()
        return plan


def test_concurrent_materialize_creates_one_task_per_date(pg_session_factory, pg_plan):
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(
            pool.map(
                lambda _: materialize_family_plans(
                    pg_session_factory, pg_plan.family_id, pg_plan.start_date
                ),
                range(2),
            )
        )

    with pg_session_factory() as db:
        assert (
            db.query(Task)
            .filter(Task.source_plan_id == pg_plan.id, Task.date == pg_plan.start_date)
            .count()
            == 1
        )
    assert sum(result.created_count for result in results) == 1
    assert all(result.failed_count == 0 for result in results)


def test_materialize_waits_for_edit_and_uses_committed_template(pg_session_factory, pg_plan):
    locked = threading.Event()
    release = threading.Event()

    def edit():
        with pg_session_factory() as db:
            plan = db.query(HomeworkPlan).filter(HomeworkPlan.id == pg_plan.id).with_for_update().one()
            locked.set()
            assert release.wait(5)
            command = HomeworkPlanUpdate(
                type=plan.type,
                title="新模板",
                desc="新说明",
                duration=20,
                subject=plan.subject,
                start_date=plan.start_date,
                end_date=plan.end_date,
                dictation_items=[{"content": "新词"}],
                updated_at=plan.updated_at,
            )
            update_plan(db, plan.id, plan.family_id, command, date(2026, 7, 10))

    with ThreadPoolExecutor(max_workers=2) as pool:
        edit_future = pool.submit(edit)
        assert locked.wait(5)
        materialize_future = pool.submit(
            materialize_family_plans, pg_session_factory, pg_plan.family_id, pg_plan.start_date
        )
        release.set()
        edit_future.result(timeout=5)
        result = materialize_future.result(timeout=5)

    assert result.created_count == 1
    with pg_session_factory() as db:
        task = db.query(Task).filter(Task.source_plan_id == pg_plan.id).one()
        assert (task.title, task.desc, task.duration) == ("新模板", "新说明", 20)
        assert [item.content for item in task.dictation_items] == ["新词"]


def test_materialize_waits_for_delete_and_creates_nothing(pg_session_factory, pg_plan):
    locked = threading.Event()
    release = threading.Event()

    def delete():
        with pg_session_factory() as db:
            db.query(HomeworkPlan).filter(HomeworkPlan.id == pg_plan.id).with_for_update().one()
            locked.set()
            assert release.wait(5)
            soft_delete_plan(db, pg_plan.id, pg_plan.family_id)

    with ThreadPoolExecutor(max_workers=2) as pool:
        delete_future = pool.submit(delete)
        assert locked.wait(5)
        materialize_future = pool.submit(
            materialize_family_plans, pg_session_factory, pg_plan.family_id, pg_plan.start_date
        )
        release.set()
        delete_future.result(timeout=5)
        result = materialize_future.result(timeout=5)

    assert result.created_count == 0
    with pg_session_factory() as db:
        assert db.query(Task).filter(Task.source_plan_id == pg_plan.id).count() == 0
