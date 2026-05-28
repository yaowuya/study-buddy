from datetime import date


def _create_graded_task(client, auth_headers, token, is_correct: bool):
    today = str(date.today())
    task = client.post("/api/v1/tasks/", json={
        "type": "school", "title": "任务", "date": today, "subject": "语文",
    }, headers=auth_headers(token)).json()
    client.patch(f"/api/v1/tasks/{task['id']}/status", json={"status": "in_progress"}, headers=auth_headers(token))
    sub = client.post("/api/v1/submissions/", json={"task_id": task["id"]}, headers=auth_headers(token)).json()
    client.post(f"/api/v1/submissions/{sub['id']}/grade", json={"is_correct": is_correct}, headers=auth_headers(token))
    return task


def test_mistakes_after_wrong_grade(client, register_and_get_token, auth_headers):
    parent_token = register_and_get_token("13800000130")
    today = str(date.today())
    task = client.post("/api/v1/tasks/", json={
        "type": "school", "title": "任务", "date": today, "subject": "数学",
    }, headers=auth_headers(parent_token)).json()
    client.patch(f"/api/v1/tasks/{task['id']}/status", json={"status": "in_progress"}, headers=auth_headers(parent_token))
    sub = client.post("/api/v1/submissions/", json={"task_id": task["id"]}, headers=auth_headers(parent_token)).json()
    client.post(f"/api/v1/submissions/{sub['id']}/grade", json={"is_correct": False}, headers=auth_headers(parent_token))
    resp = client.get("/api/v1/mistakes/", headers=auth_headers(parent_token))
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["subject"] == "数学"


def test_archive_mistake(client, register_and_get_token, auth_headers):
    parent_token = register_and_get_token("13800000131")
    _create_graded_task(client, auth_headers, parent_token, is_correct=False)
    mistakes = client.get("/api/v1/mistakes/", headers=auth_headers(parent_token)).json()
    resp = client.post(f"/api/v1/mistakes/{mistakes[0]['id']}/archive", headers=auth_headers(parent_token))
    assert resp.status_code == 200
    assert resp.json()["archived"] is True


def test_no_mistakes_for_correct_grade(client, register_and_get_token, auth_headers):
    parent_token = register_and_get_token("13800000132")
    _create_graded_task(client, auth_headers, parent_token, is_correct=True)
    resp = client.get("/api/v1/mistakes/", headers=auth_headers(parent_token))
    assert len(resp.json()) == 0
