import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# 测试环境强制使用固定初始密码，不受 .env 影响
os.environ.setdefault("ADMIN_INITIAL_PASSWORD", "admin123")

from app.database import Base
from app.main import app
from app.core.deps import get_db
from app.crud.admin import seed_admin

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

# 在测试 DB 中种入默认管理员
_seed_db = TestSessionLocal()
seed_admin(_seed_db)
_seed_db.close()


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def register_and_get_token(client):
    def _register(phone: str, role: str = "parent") -> str:
        resp = client.post("/api/v1/auth/register", json={
            "phone": phone,
            "password": "test1234",
            "role": role,
        })
        return resp.json()["access_token"]
    return _register


@pytest.fixture
def auth_headers():
    def _headers(token: str) -> dict:
        return {"Authorization": f"Bearer {token}"}
    return _headers
