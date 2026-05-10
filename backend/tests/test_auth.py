def test_register_parent(client):
    resp = client.post("/api/v1/auth/register", json={
        "phone": "13800000001",
        "password": "test1234",
        "role": "parent",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data


def test_register_student(client):
    resp = client.post("/api/v1/auth/register", json={
        "phone": "13800000002",
        "password": "test1234",
        "role": "student",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data


def test_register_duplicate_phone(client):
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


def test_login_success(client):
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


def test_login_wrong_password(client):
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


def test_get_me(client):
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


def test_get_me_no_token(client):
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401
