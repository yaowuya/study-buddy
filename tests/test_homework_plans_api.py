from datetime import date

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
