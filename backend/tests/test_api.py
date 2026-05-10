import uuid
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.main import app
from app.core.deps import get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# --- Auth tests ---

def test_register_parent():
    resp = client.post("/api/v1/auth/register", json={
        "phone": "13800000001",
        "password": "test1234",
        "role": "parent",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data


def test_register_student():
    resp = client.post("/api/v1/auth/register", json={
        "phone": "13800000002",
        "password": "test1234",
        "role": "student",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data


def test_register_duplicate_phone():
    client.post("/api/v1/auth/register", json={
        "phone": "13800000003",
        "password": "test1234",
        "role": "parent",
    })
    resp = client.post("/api/v1/auth/register", json={
        "phone": "13800000003",
        "password": "test1234",
        "role": "parent",
    })
    assert resp.status_code == 400


def test_login_success():
    client.post("/api/v1/auth/register", json={
        "phone": "13800000004",
        "password": "test1234",
        "role": "parent",
    })
    resp = client.post("/api/v1/auth/login", json={
        "phone": "13800000004",
        "password": "test1234",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password():
    client.post("/api/v1/auth/register", json={
        "phone": "13800000005",
        "password": "test1234",
        "role": "parent",
    })
    resp = client.post("/api/v1/auth/login", json={
        "phone": "13800000005",
        "password": "wrongpass",
    })
    assert resp.status_code == 401


def test_get_me():
    reg = client.post("/api/v1/auth/register", json={
        "phone": "13800000006",
        "password": "test1234",
        "role": "parent",
    })
    token = reg.json()["access_token"]
    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["phone"] == "13800000006"
    assert resp.json()["role"] == "parent"


def test_get_me_no_token():
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401


# --- Helpers ---

def register_and_get_token(phone: str, role: str = "parent") -> str:
    resp = client.post("/api/v1/auth/register", json={
        "phone": phone,
        "password": "test1234",
        "role": role,
    })
    return resp.json()["access_token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# --- Task tests ---

def test_create_task():
    token = register_and_get_token("13800000100")
    resp = client.post("/api/v1/tasks/", json={
        "type": "school",
        "title": "语文作业",
        "desc": "完成第5课练习",
        "duration": 30,
        "date": str(date.today()),
        "subject": "语文",
    }, headers=auth_headers(token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "语文作业"
    assert data["type"] == "school"
    assert data["status"] == "pending"


def test_list_tasks():
    token = register_and_get_token("13800000101")
    today = str(date.today())
    client.post("/api/v1/tasks/", json={
        "type": "school", "title": "任务1", "date": today,
    }, headers=auth_headers(token))
    client.post("/api/v1/tasks/", json={
        "type": "home", "title": "任务2", "date": today,
    }, headers=auth_headers(token))
    resp = client.get(f"/api/v1/tasks/?task_date={today}", headers=auth_headers(token))
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_update_task_status():
    token = register_and_get_token("13800000102")
    today = str(date.today())
    task = client.post("/api/v1/tasks/", json={
        "type": "school", "title": "任务", "date": today,
    }, headers=auth_headers(token)).json()
    resp = client.patch(f"/api/v1/tasks/{task['id']}/status", json={
        "status": "in_progress",
    }, headers=auth_headers(token))
    assert resp.status_code == 200
    assert resp.json()["status"] == "in_progress"


def test_delete_task():
    token = register_and_get_token("13800000103")
    today = str(date.today())
    task = client.post("/api/v1/tasks/", json={
        "type": "school", "title": "任务", "date": today,
    }, headers=auth_headers(token)).json()
    resp = client.delete(f"/api/v1/tasks/{task['id']}", headers=auth_headers(token))
    assert resp.status_code == 200


def test_student_cannot_create_task():
    token = register_and_get_token("13800000104", role="student")
    resp = client.post("/api/v1/tasks/", json={
        "type": "school", "title": "任务", "date": str(date.today()),
    }, headers=auth_headers(token))
    assert resp.status_code == 403


# --- Dictation tests ---

def test_create_and_get_dictation_items():
    token = register_and_get_token("13800000110")
    today = str(date.today())
    task = client.post("/api/v1/tasks/", json={
        "type": "school", "title": "听写", "date": today, "subject": "语文",
    }, headers=auth_headers(token)).json()
    items = [
        {"content": "春天", "speed": 1.0, "pause_interval": 3},
        {"content": "花朵", "speed": 0.8, "pause_interval": 5},
    ]
    resp = client.post("/api/v1/dictation/", json={
        "task_id": task["id"], "items": items,
    }, headers=auth_headers(token))
    assert resp.status_code == 200
    assert len(resp.json()) == 2

    get_resp = client.get(f"/api/v1/dictation/{task['id']}", headers=auth_headers(token))
    assert get_resp.status_code == 200
    assert len(get_resp.json()) == 2
    contents = [item["content"] for item in get_resp.json()]
    assert "春天" in contents
    assert "花朵" in contents


# --- Submission tests ---

def test_submit_task():
    token = register_and_get_token("13800000120")
    today = str(date.today())
    task = client.post("/api/v1/tasks/", json={
        "type": "school", "title": "任务", "date": today,
    }, headers=auth_headers(token)).json()
    # Update to in_progress first
    client.patch(f"/api/v1/tasks/{task['id']}/status", json={"status": "in_progress"}, headers=auth_headers(token))
    resp = client.post("/api/v1/submissions/", json={
        "task_id": task["id"],
    }, headers=auth_headers(token))
    assert resp.status_code == 200
    assert resp.json()["is_correct"] is None


def test_grade_submission():
    parent_token = register_and_get_token("13800000121")
    today = str(date.today())
    task = client.post("/api/v1/tasks/", json={
        "type": "school", "title": "任务", "date": today,
    }, headers=auth_headers(parent_token)).json()
    client.patch(f"/api/v1/tasks/{task['id']}/status", json={"status": "in_progress"}, headers=auth_headers(parent_token))
    sub = client.post("/api/v1/submissions/", json={
        "task_id": task["id"],
    }, headers=auth_headers(parent_token)).json()
    resp = client.post(f"/api/v1/submissions/{sub['id']}/grade", json={
        "is_correct": False, "comment": "注意审题",
    }, headers=auth_headers(parent_token))
    assert resp.status_code == 200
    assert resp.json()["is_correct"] is False


def test_double_submit():
    token = register_and_get_token("13800000122")
    today = str(date.today())
    task = client.post("/api/v1/tasks/", json={
        "type": "school", "title": "任务", "date": today,
    }, headers=auth_headers(token)).json()
    client.patch(f"/api/v1/tasks/{task['id']}/status", json={"status": "in_progress"}, headers=auth_headers(token))
    client.post("/api/v1/submissions/", json={"task_id": task["id"]}, headers=auth_headers(token))
    resp = client.post("/api/v1/submissions/", json={"task_id": task["id"]}, headers=auth_headers(token))
    assert resp.status_code == 400


# --- Mistake tests ---

def test_mistakes_after_wrong_grade():
    parent_token = register_and_get_token("13800000130")
    today = str(date.today())
    task = client.post("/api/v1/tasks/", json={
        "type": "school", "title": "任务", "date": today, "subject": "数学",
    }, headers=auth_headers(parent_token)).json()
    client.patch(f"/api/v1/tasks/{task['id']}/status", json={"status": "in_progress"}, headers=auth_headers(parent_token))
    sub = client.post("/api/v1/submissions/", json={"task_id": task["id"]}, headers=auth_headers(parent_token)).json()
    client.post(f"/api/v1/submissions/{sub['id']}/grade", json={
        "is_correct": False,
    }, headers=auth_headers(parent_token))
    resp = client.get("/api/v1/mistakes/", headers=auth_headers(parent_token))
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["subject"] == "数学"


def test_archive_mistake():
    parent_token = register_and_get_token("13800000131")
    today = str(date.today())
    task = client.post("/api/v1/tasks/", json={
        "type": "school", "title": "任务", "date": today, "subject": "语文",
    }, headers=auth_headers(parent_token)).json()
    client.patch(f"/api/v1/tasks/{task['id']}/status", json={"status": "in_progress"}, headers=auth_headers(parent_token))
    sub = client.post("/api/v1/submissions/", json={"task_id": task["id"]}, headers=auth_headers(parent_token)).json()
    client.post(f"/api/v1/submissions/{sub['id']}/grade", json={"is_correct": False}, headers=auth_headers(parent_token))
    mistakes = client.get("/api/v1/mistakes/", headers=auth_headers(parent_token)).json()
    resp = client.post(f"/api/v1/mistakes/{mistakes[0]['id']}/archive", headers=auth_headers(parent_token))
    assert resp.status_code == 200
    assert resp.json()["archived"] is True


def test_no_mistakes_for_correct_grade():
    parent_token = register_and_get_token("13800000132")
    today = str(date.today())
    task = client.post("/api/v1/tasks/", json={
        "type": "school", "title": "任务", "date": today,
    }, headers=auth_headers(parent_token)).json()
    client.patch(f"/api/v1/tasks/{task['id']}/status", json={"status": "in_progress"}, headers=auth_headers(parent_token))
    sub = client.post("/api/v1/submissions/", json={"task_id": task["id"]}, headers=auth_headers(parent_token)).json()
    client.post(f"/api/v1/submissions/{sub['id']}/grade", json={"is_correct": True}, headers=auth_headers(parent_token))
    resp = client.get("/api/v1/mistakes/", headers=auth_headers(parent_token))
    assert len(resp.json()) == 0


# --- Cross-family isolation test ---

def test_cannot_access_other_family_task():
    token_a = register_and_get_token("13800000140")
    token_b = register_and_get_token("13800000141")
    today = str(date.today())
    task = client.post("/api/v1/tasks/", json={
        "type": "school", "title": "A的任务", "date": today,
    }, headers=auth_headers(token_a)).json()
    resp = client.get(f"/api/v1/tasks/{task['id']}", headers=auth_headers(token_b))
    assert resp.status_code == 404
