"""
Admin 系统测试：认证、用户/家庭/任务管理、软删除、权限隔离
"""
import pytest
from fastapi.testclient import TestClient


# ─── 工具函数 ───

def admin_login(client: TestClient, username="admin", password="admin123") -> str:
    resp = client.post("/api/v1/admin/auth/login", json={"username": username, "password": password})
    assert resp.status_code == 200, f"admin login failed: {resp.text}"
    return resp.json()["access_token"]


def admin_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def register_user(client: TestClient, phone: str, role: str = "parent") -> str:
    resp = client.post("/api/v1/auth/register", json={
        "phone": phone, "password": "test1234", "role": role,
    })
    assert resp.status_code == 200
    return resp.json()["access_token"]


# ─── 管理员认证 ───

def test_admin_login_success(client):
    token = admin_login(client)
    assert token


def test_admin_login_wrong_password(client):
    resp = client.post("/api/v1/admin/auth/login", json={"username": "admin", "password": "wrong"})
    assert resp.status_code == 401


def test_admin_me(client):
    token = admin_login(client)
    resp = client.get("/api/v1/admin/auth/me", headers=admin_headers(token))
    assert resp.status_code == 200
    assert resp.json()["username"] == "admin"


def test_admin_change_password(client):
    token = admin_login(client)
    resp = client.patch("/api/v1/admin/auth/password", json={
        "old_password": "admin123", "new_password": "newpass456",
    }, headers=admin_headers(token))
    assert resp.status_code == 200
    # 验证新密码可登录
    new_token = admin_login(client, password="newpass456")
    assert new_token
    # 改回原密码，不影响其他测试
    client.patch("/api/v1/admin/auth/password", json={
        "old_password": "newpass456", "new_password": "admin123",
    }, headers=admin_headers(new_token))


def test_admin_change_password_wrong_old(client):
    token = admin_login(client)
    resp = client.patch("/api/v1/admin/auth/password", json={
        "old_password": "wrongold", "new_password": "newpass123",  # min_length=8
    }, headers=admin_headers(token))
    assert resp.status_code == 400


def test_non_admin_token_blocked(client):
    """普通用户 token 不能访问 admin 接口"""
    user_token = register_user(client, "13900000010")
    resp = client.get("/api/v1/admin/auth/me", headers={"Authorization": f"Bearer {user_token}"})
    assert resp.status_code == 403


def test_admin_token_blocked_on_user_endpoints(client):
    """admin token 不能访问用户端接口"""
    token = admin_login(client)
    resp = client.get("/api/v1/auth/me", headers=admin_headers(token))
    assert resp.status_code == 403


# ─── 用户管理 ───

def test_admin_list_users(client):
    register_user(client, "13900000011")
    token = admin_login(client)
    resp = client.get("/api/v1/admin/users/", headers=admin_headers(token))
    assert resp.status_code == 200
    data = resp.json()
    assert "total" in data and "items" in data


def test_admin_list_users_filter_by_role(client):
    register_user(client, "13900000012", role="student")
    token = admin_login(client)
    resp = client.get("/api/v1/admin/users/?role=student", headers=admin_headers(token))
    assert resp.status_code == 200
    for item in resp.json()["items"]:
        assert item["role"] == "student"


def test_admin_get_user_detail(client):
    user_token = register_user(client, "13900000013")
    user_id = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {user_token}"}).json()["id"]
    token = admin_login(client)
    resp = client.get(f"/api/v1/admin/users/{user_id}", headers=admin_headers(token))
    assert resp.status_code == 200
    assert resp.json()["phone"] == "13900000013"


def test_admin_update_user_active(client):
    user_token = register_user(client, "13900000014")
    user_id = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {user_token}"}).json()["id"]
    token = admin_login(client)
    # 禁用
    resp = client.patch(f"/api/v1/admin/users/{user_id}", json={"is_active": False}, headers=admin_headers(token))
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False
    # 被禁用用户无法登录
    resp2 = client.post("/api/v1/auth/login", json={"phone": "13900000014", "password": "test1234"})
    assert resp2.status_code == 403


def test_admin_soft_delete_user(client):
    user_token = register_user(client, "13900000015")
    user_id = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {user_token}"}).json()["id"]
    token = admin_login(client)
    # 软删除
    resp = client.delete(f"/api/v1/admin/users/{user_id}", headers=admin_headers(token))
    assert resp.status_code == 200
    # 用户端查不到（软删除过滤）
    resp2 = client.post("/api/v1/auth/login", json={"phone": "13900000015", "password": "test1234"})
    assert resp2.status_code in (401, 403)


# ─── 家庭管理 ───

def test_admin_list_families(client):
    register_user(client, "13900000016")  # 注册时自动创建家庭
    token = admin_login(client)
    resp = client.get("/api/v1/admin/families/", headers=admin_headers(token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1


def test_admin_get_family_detail(client):
    user_token = register_user(client, "13900000017")
    family_id = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {user_token}"}).json()["family_id"]
    token = admin_login(client)
    resp = client.get(f"/api/v1/admin/families/{family_id}", headers=admin_headers(token))
    assert resp.status_code == 200
    assert "members" in resp.json()


def test_admin_soft_delete_family(client):
    user_token = register_user(client, "13900000018")
    family_id = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {user_token}"}).json()["family_id"]
    token = admin_login(client)
    resp = client.delete(f"/api/v1/admin/families/{family_id}", headers=admin_headers(token))
    assert resp.status_code == 200


# ─── 任务管理 ───

def test_admin_list_tasks(client):
    from datetime import date
    user_token = register_user(client, "13900000019")
    client.post("/api/v1/tasks/", json={"type": "school", "title": "测试任务", "date": str(date.today())},
                headers={"Authorization": f"Bearer {user_token}"})
    token = admin_login(client)
    resp = client.get("/api/v1/admin/tasks/", headers=admin_headers(token))
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1


def test_admin_soft_delete_task(client):
    from datetime import date
    user_token = register_user(client, "13900000020")
    task = client.post("/api/v1/tasks/", json={"type": "school", "title": "待删任务", "date": str(date.today())},
                       headers={"Authorization": f"Bearer {user_token}"}).json()
    token = admin_login(client)
    resp = client.delete(f"/api/v1/admin/tasks/{task['id']}", headers=admin_headers(token))
    assert resp.status_code == 200
    # 用户端查不到
    resp2 = client.get("/api/v1/tasks/", headers={"Authorization": f"Bearer {user_token}"})
    ids = [t["id"] for t in resp2.json()]
    assert task["id"] not in ids


# ─── 统计接口 ───

def test_admin_stats(client):
    token = admin_login(client)
    resp = client.get("/api/v1/admin/tasks/stats", headers=admin_headers(token))
    assert resp.status_code == 200
    data = resp.json()
    assert all(k in data for k in ["total_users", "total_families", "today_tasks", "pending_submissions"])
