from datetime import date, timedelta

from app.api.v1 import homework_plans as plans_api
from app.database import SessionLocal
from app.models.homework_plan import HomeworkPlan
from app.models.task import Task


def _register_family(client, register_and_get_token, auth_headers, suffix: str):
    parent_token = register_and_get_token(f"1391000{suffix}", "parent")
    parent_headers = auth_headers(parent_token)
    family = client.get("/api/v1/auth/family", headers=parent_headers).json()
    student_token = register_and_get_token(f"1381000{suffix}", "student")
    student_headers = auth_headers(student_token)
    client.post("/api/v1/auth/student-bind", headers=student_headers, json={"code": family["code"]})
    return parent_headers, student_headers


def test_parent_creates_lists_and_gets_plan(client, register_and_get_token, auth_headers, monkeypatch):
    parent_headers, _ = _register_family(client, register_and_get_token, auth_headers, "0001")
    today = date(2026, 7, 11)
    monkeypatch.setattr(plans_api, "business_today", lambda: today)
    monkeypatch.setattr(plans_api, "materialize_family_plans", lambda *_: None)

    response = client.post(
        "/api/v1/homework-plans/",
        headers=parent_headers,
        json={"type": "home", "title": "每日阅读", "range_type": "week", "dictation_items": []},
    )
    assert response.status_code == 200, response.text
    plan = response.json()
    assert plan["start_date"] == today.isoformat()
    assert plan["end_date"] == date(2026, 7, 17).isoformat()

    listed = client.get("/api/v1/homework-plans/", headers=parent_headers)
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()] == [plan["id"]]

    detail = client.get(f"/api/v1/homework-plans/{plan['id']}", headers=parent_headers)
    assert detail.status_code == 200
    assert detail.json()["title"] == "每日阅读"


def test_plan_management_requires_parent_and_family_scope(client, register_and_get_token, auth_headers, monkeypatch):
    parent_a, student_a = _register_family(client, register_and_get_token, auth_headers, "0002")
    parent_b, _ = _register_family(client, register_and_get_token, auth_headers, "0003")
    monkeypatch.setattr(plans_api, "business_today", lambda: date(2026, 7, 11))
    monkeypatch.setattr(plans_api, "materialize_family_plans", lambda *_: None)
    plan = client.post(
        "/api/v1/homework-plans/",
        headers=parent_a,
        json={"type": "home", "title": "计划", "range_type": "week"},
    ).json()

    assert client.get("/api/v1/homework-plans/", headers=student_a).status_code == 403
    assert client.get(f"/api/v1/homework-plans/{plan['id']}", headers=parent_b).status_code == 404


def _full_update(plan: dict, **overrides):
    payload = {
        "type": plan["type"],
        "title": plan["title"],
        "desc": plan["desc"],
        "duration": plan["duration"],
        "subject": plan["subject"],
        "start_date": plan["start_date"],
        "end_date": plan["end_date"],
        "updated_at": plan["updated_at"],
        "dictation_items": plan.get("dictation_items", []),
    }
    payload.update(overrides)
    return payload


def test_patch_conflict_update_and_idempotent_delete(client, register_and_get_token, auth_headers, monkeypatch):
    parent_headers, _ = _register_family(client, register_and_get_token, auth_headers, "0005")
    today = date(2026, 7, 11)
    monkeypatch.setattr(plans_api, "business_today", lambda: today)
    monkeypatch.setattr(plans_api, "materialize_family_plans", lambda *_: None)
    plan = client.post(
        "/api/v1/homework-plans/",
        headers=parent_headers,
        json={"type": "home", "title": "旧标题", "range_type": "week"},
    ).json()

    stale = client.patch(
        f"/api/v1/homework-plans/{plan['id']}",
        headers=parent_headers,
        json=_full_update(plan, title="新标题", updated_at="2000-01-01T00:00:00Z"),
    )
    assert stale.status_code == 409

    updated = client.patch(
        f"/api/v1/homework-plans/{plan['id']}",
        headers=parent_headers,
        json=_full_update(plan, title="新标题"),
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["title"] == "新标题"

    first = client.delete(f"/api/v1/homework-plans/{plan['id']}", headers=parent_headers)
    second = client.delete(f"/api/v1/homework-plans/{plan['id']}", headers=parent_headers)
    assert first.status_code == 200
    assert second.status_code == 200
    assert client.get(f"/api/v1/homework-plans/{plan['id']}", headers=parent_headers).status_code == 404


def test_started_plan_rejects_start_date_change(client, register_and_get_token, auth_headers, monkeypatch):
    parent_headers, _ = _register_family(client, register_and_get_token, auth_headers, "0006")
    today = date(2026, 7, 11)
    monkeypatch.setattr(plans_api, "business_today", lambda: today)
    monkeypatch.setattr(plans_api, "materialize_family_plans", lambda *_: None)
    plan = client.post(
        "/api/v1/homework-plans/",
        headers=parent_headers,
        json={"type": "home", "title": "计划", "range_type": "week"},
    ).json()
    changed = client.patch(
        f"/api/v1/homework-plans/{plan['id']}",
        headers=parent_headers,
        json=_full_update(plan, start_date=(today + timedelta(days=1)).isoformat()),
    )
    assert changed.status_code == 422


def test_plan_template_never_appears_in_task_list(client, register_and_get_token, auth_headers, monkeypatch):
    parent_headers, _ = _register_family(client, register_and_get_token, auth_headers, "0004")
    monkeypatch.setattr(plans_api, "business_today", lambda: date(2026, 7, 11))
    monkeypatch.setattr(plans_api, "materialize_family_plans", lambda *_: None)
    created = client.post(
        "/api/v1/homework-plans/",
        headers=parent_headers,
        json={"type": "home", "title": "模板", "range_type": "week"},
    )
    assert created.status_code == 200
    tasks = client.get("/api/v1/tasks/", headers=parent_headers).json()
    assert all(task["title"] != "模板" for task in tasks)
