import re
from pathlib import Path


def test_container_name_uses_only_docker_allowed_characters():
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")
    match = re.search(r"^\s*container_name:\s*(\S+)\s*$", compose, re.MULTILINE)

    assert match is not None
    assert re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_.-]*", match.group(1))
