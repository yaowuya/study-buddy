from datetime import date


def test_create_and_get_dictation_items(client, register_and_get_token, auth_headers):
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
