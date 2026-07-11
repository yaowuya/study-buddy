from datetime import date, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.models.task import TaskType
from app.schemas.homework_plan import (
    HomeworkPlanCreate,
    HomeworkPlanDetailOut,
    HomeworkPlanOut,
    HomeworkPlanUpdate,
    MaterializeResult,
    PlanMaterializeResult,
)


def test_create_ranges_and_dictation_validation():
    today = date(2026, 7, 11)
    week = HomeworkPlanCreate(
        type="home",
        title="练习",
        range_type="week",
        start_date=date(2000, 1, 1),
        end_date=date(2000, 1, 2),
    )
    month = HomeworkPlanCreate(type="school", title="阅读", range_type="month")

    assert week.resolve_dates(today) == (today, date(2026, 7, 17))
    assert month.resolve_dates(today) == (today, date(2026, 8, 9))

    custom = HomeworkPlanCreate(
        type="home",
        title="听写",
        range_type="custom",
        start_date=today,
        end_date=date(2026, 7, 12),
        dictation_items=[{"content": "  春天  "}, {"content": "夏天"}],
    )
    assert custom.resolve_dates(today) == (today, date(2026, 7, 12))
    assert [item.content for item in custom.dictation_items] == ["春天", "夏天"]

    with pytest.raises(ValidationError):
        HomeworkPlanCreate(
            type="home",
            title="听写",
            range_type="custom",
            start_date=today,
            end_date=today,
            dictation_items=[{"content": "词"}, {"content": " 词 "}],
        )


@pytest.mark.parametrize(
    "payload",
    [
        {"range_type": "custom", "start_date": None, "end_date": date(2026, 7, 11)},
        {"range_type": "custom", "start_date": date(2026, 7, 10), "end_date": date(2026, 7, 11)},
        {"range_type": "custom", "start_date": date(2026, 7, 12), "end_date": date(2026, 7, 11)},
        {"range_type": "custom", "start_date": date(2026, 7, 11), "end_date": date(2027, 7, 12)},
    ],
)
def test_custom_range_validation(payload):
    with pytest.raises((ValidationError, ValueError)):
        command = HomeworkPlanCreate(type="home", title="练习", **payload)
        command.resolve_dates(date(2026, 7, 11))


def test_create_field_constraints():
    for payload in (
        {"title": "   "},
        {"title": "练习", "duration": 0},
        {"title": "练习", "dictation_items": [{"content": "   "}]},
    ):
        with pytest.raises(ValidationError):
            HomeworkPlanCreate(type="home", range_type="week", **payload)


def test_update_requires_complete_payload_and_token():
    valid = {
        "type": "home",
        "title": "每日听写",
        "desc": None,
        "duration": 20,
        "subject": "语文",
        "start_date": date(2026, 7, 11),
        "end_date": date(2026, 7, 17),
        "dictation_items": [{"content": " 春天 "}],
        "updated_at": datetime(2026, 7, 11, 1, 2, 3),
    }
    update = HomeworkPlanUpdate(**valid)
    assert update.dictation_items[0].content == "春天"

    for missing in valid:
        with pytest.raises(ValidationError):
            HomeworkPlanUpdate(**{key: value for key, value in valid.items() if key != missing})


def test_output_and_materialize_contracts():
    now = datetime(2026, 7, 11, 1, 2, 3)
    common = {
        "id": uuid4(),
        "type": TaskType.HOME,
        "title": "练习",
        "desc": None,
        "duration": None,
        "subject": None,
        "start_date": date(2026, 7, 11),
        "end_date": date(2026, 7, 17),
        "status": "active",
        "has_dictation": True,
        "dictation_count": 1,
        "total_days": 7,
        "generated_count": 1,
        "remaining_days": 6,
        "days_until_start": None,
        "today_generated": True,
        "updated_at": now,
    }
    assert HomeworkPlanOut(**common).status == "active"
    detail = HomeworkPlanDetailOut(**common, dictation_items=[{"content": "词"}])
    assert detail.dictation_items[0].content == "词"

    plan_id = uuid4()
    result = MaterializeResult.from_plans(
        [
            PlanMaterializeResult.success(plan_id, [date(2026, 7, 11)]),
            PlanMaterializeResult.failed(uuid4(), "plan_unavailable"),
        ]
    )
    assert (result.created_count, result.success_count, result.failed_count) == (1, 1, 1)
    assert result.plans[1].error == "plan_unavailable"
