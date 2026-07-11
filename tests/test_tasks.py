from datetime import date, timedelta


def test_create_task(client, register_and_get_token, auth_headers):
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
    assert data["source_plan_id"] is None


def test_list_tasks(client, register_and_get_token, auth_headers):
    token = register_and_get_token("13800000101")
    today = str(date.today())
    client.post("/api/v1/tasks/", json={
        "type": "school", "title": "任务1", "date": today,
    }, headers=auth_headers(token))
    client.post("/api/v1/tasks/", json={
        "type": "home", "title": "任务2", "date": today,
    }, headers=auth_headers(token))
    resp = client.get(f"/api/v1/tasks/?date_from={today}&date_to={today}", headers=auth_headers(token))
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_update_task_status(client, register_and_get_token, auth_headers):
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


def test_delete_task(client, register_and_get_token, auth_headers):
    token = register_and_get_token("13800000103")
    today = str(date.today())
    task = client.post("/api/v1/tasks/", json={
        "type": "school", "title": "任务", "date": today,
    }, headers=auth_headers(token)).json()
    resp = client.delete(f"/api/v1/tasks/{task['id']}", headers=auth_headers(token))
    assert resp.status_code == 200


def test_student_cannot_create_task(client, register_and_get_token, auth_headers):
    token = register_and_get_token("13800000104", role="student")
    resp = client.post("/api/v1/tasks/", json={
        "type": "school", "title": "任务", "date": str(date.today()),
    }, headers=auth_headers(token))
    assert resp.status_code == 403


def test_list_tasks_by_task_date(client, register_and_get_token, auth_headers):
    """task_date 快捷参数：只返回指定日期的任务，跨日任务不应出现"""
    token = register_and_get_token("13800000142")
    today = str(date.today())
    yesterday = str(date.today() - timedelta(days=1))
    client.post("/api/v1/tasks/", json={
        "type": "school", "title": "今日任务", "date": today,
    }, headers=auth_headers(token))
    client.post("/api/v1/tasks/", json={
        "type": "home", "title": "昨日任务", "date": yesterday,
    }, headers=auth_headers(token))
    resp = client.get(f"/api/v1/tasks/?task_date={today}", headers=auth_headers(token))
    assert resp.status_code == 200
    tasks = resp.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "今日任务"


def test_cannot_access_other_family_task(client, register_and_get_token, auth_headers):
    token_a = register_and_get_token("13800000140")
    token_b = register_and_get_token("13800000141")
    today = str(date.today())
    task = client.post("/api/v1/tasks/", json={
        "type": "school", "title": "A的任务", "date": today,
    }, headers=auth_headers(token_a)).json()
    resp = client.get(f"/api/v1/tasks/{task['id']}", headers=auth_headers(token_b))
    assert resp.status_code == 404
