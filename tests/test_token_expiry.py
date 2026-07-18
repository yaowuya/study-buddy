from datetime import datetime, timedelta, timezone
from pathlib import Path

from jose import jwt

from app.core import security
from app.core.config import Settings


def test_default_client_access_token_expires_after_30_days(monkeypatch):
    monkeypatch.delenv("ACCESS_TOKEN_EXPIRE_MINUTES", raising=False)
    default_settings = Settings(_env_file=None)
    monkeypatch.setattr(security, "settings", default_settings)
    issued_at = datetime.now(timezone.utc)

    token = security.create_access_token("expiry-check")
    issued_after = datetime.now(timezone.utc)
    payload = jwt.decode(token, default_settings.SECRET_KEY, algorithms=["HS256"])
    expires_at = datetime.fromtimestamp(payload["exp"], timezone.utc)

    assert issued_at + timedelta(days=30, seconds=-1) <= expires_at
    assert expires_at <= issued_after + timedelta(days=30)


def test_admin_access_token_default_remains_eight_hours(monkeypatch):
    monkeypatch.delenv("ADMIN_TOKEN_EXPIRE_MINUTES", raising=False)
    default_settings = Settings(_env_file=None)

    assert default_settings.ADMIN_TOKEN_EXPIRE_MINUTES == 60 * 8


def test_env_example_documents_30_day_client_token():
    env_example = Path(__file__).parents[1] / ".env.example"

    assert "ACCESS_TOKEN_EXPIRE_MINUTES=43200" in env_example.read_text(encoding="utf-8")
