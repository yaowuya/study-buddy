from datetime import date


def test_submit_task(client, register_and_get_token, auth_headers):
    token = register_and_get_token("13800000120")
    today = str(date.today())
    task = client.post("/api/v1/tasks/", json={
        "type": "school", "title": "任务", "date": today,
    }, headers=auth_headers(token)).json()
    client.patch(f"/api/v1/tasks/{task['id']}/status", json={"status": "in_progress"}, headers=auth_headers(token))
    resp = client.post("/api/v1/submissions/", json={
        "task_id": task["id"],
    }, headers=auth_headers(token))
    assert resp.status_code == 200
    assert resp.json()["is_correct"] is None


def test_grade_submission(client, register_and_get_token, auth_headers):
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


def test_double_submit(client, register_and_get_token, auth_headers):
    token = register_and_get_token("13800000122")
    today = str(date.today())
    task = client.post("/api/v1/tasks/", json={
        "type": "school", "title": "任务", "date": today,
    }, headers=auth_headers(token)).json()
    client.patch(f"/api/v1/tasks/{task['id']}/status", json={"status": "in_progress"}, headers=auth_headers(token))
    client.post("/api/v1/submissions/", json={"task_id": task["id"]}, headers=auth_headers(token))
    resp = client.post("/api/v1/submissions/", json={"task_id": task["id"]}, headers=auth_headers(token))
    assert resp.status_code == 400
