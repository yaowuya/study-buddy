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


def test_login_returns_correct_role(client):
    """验证登录后获取的用户信息角色正确，防止跨角色登录漏洞"""
    # 注册家长账号
    client.post("/api/v1/auth/register", json={
        "phone": "13800000007",
        "password": "test1234",
        "role": "parent",
    })
    # 登录家长账号
    login_resp = client.post("/api/v1/auth/login", json={
        "phone": "13800000007",
        "password": "test1234",
    })
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    # 获取用户信息，验证角色确实是 parent
    me_resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["role"] == "parent"


def test_login_student_returns_student_role(client):
    """验证学生账号登录后角色是 student"""
    # 注册学生账号
    client.post("/api/v1/auth/register", json={
        "phone": "13800000008",
        "password": "test1234",
        "role": "student",
    })
    # 登录学生账号
    login_resp = client.post("/api/v1/auth/login", json={
        "phone": "13800000008",
        "password": "test1234",
    })
    token = login_resp.json()["access_token"]

    # 验证角色是 student
    me_resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.json()["role"] == "student"
