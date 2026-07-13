import re
from pathlib import Path


def test_container_name_uses_only_docker_allowed_characters():
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")
    match = re.search(r"^\s*container_name:\s*(\S+)\s*$", compose, re.MULTILINE)

    assert match is not None
    assert re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_.-]*", match.group(1))


def test_compose_uses_release_image_stable_name_and_healthcheck():
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")

    assert "image: studybuddy-api:1.2.0" in compose
    assert "container_name: studybuddy-api\n" in compose
    assert "studybuddy-api-2.0" not in compose
    assert "healthcheck:" in compose
    assert "http://127.0.0.1:8000/health" in compose
