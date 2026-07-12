import json
import re
from pathlib import Path

from fastapi.testclient import TestClient

from app.core.version import APP_VERSION
from app.main import app

EXPECTED_VERSION = "1.2.0"


def read_json_with_comments(path: str) -> dict:
    text = Path(path).read_text(encoding="utf-8")
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r"//.*", "", text)
    return json.loads(text)


def test_runtime_version_and_health_endpoint_are_current():
    assert APP_VERSION == EXPECTED_VERSION
    assert app.version == EXPECTED_VERSION
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": EXPECTED_VERSION}


def test_frontend_package_versions_match_release():
    client_manifest = read_json_with_comments("client/src/manifest.json")
    client_package = json.loads(Path("client/package.json").read_text(encoding="utf-8"))
    client_lock = json.loads(Path("client/package-lock.json").read_text(encoding="utf-8"))
    admin_package = json.loads(Path("admin/package.json").read_text(encoding="utf-8"))
    admin_lock = json.loads(Path("admin/package-lock.json").read_text(encoding="utf-8"))

    assert client_manifest["versionName"] == EXPECTED_VERSION
    assert client_manifest["versionCode"] == "120"
    for package in (client_package, client_lock, admin_package, admin_lock):
        assert package["version"] == EXPECTED_VERSION
    assert client_lock["packages"][""]["version"] == EXPECTED_VERSION
    assert admin_lock["packages"][""]["version"] == EXPECTED_VERSION
