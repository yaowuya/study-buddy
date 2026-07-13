from pathlib import Path


def _active_dockerignore_entries() -> set[str]:
    return {
        line.strip()
        for line in Path(".dockerignore").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }


def test_entrypoint_has_stdout_fallback_when_log_dir_is_not_writable():
    script = Path("docker-entrypoint.sh").read_text(encoding="utf-8")

    assert "-w \"$LOG_DIR\"" in script
    assert "--access-logfile -" in script
    assert "--error-logfile -" in script


def test_dockerfile_uses_requirements_once_and_labels_release_version():
    dockerfile = Path("Dockerfile").read_text(encoding="utf-8")

    assert "ARG APP_VERSION=1.2.0" in dockerfile
    assert "ENV APP_VERSION=$APP_VERSION" in dockerfile
    assert 'org.opencontainers.image.version="$APP_VERSION"' in dockerfile
    assert "pip install --no-cache-dir -r requirements.txt\n" in dockerfile
    assert "-r requirements.txt gunicorn" not in dockerfile


def test_migration_doc_mentions_docker_database_url_encoding():
    doc = Path("docs/postgresql-to-mysql-migration.md").read_text(encoding="utf-8")

    assert "host.docker.internal" in doc
    assert "%40" in doc
    assert "Cai" not in doc
    assert "180906" not in doc

def test_alembic_env_does_not_write_database_url_through_configparser():
    env = Path("alembic/env.py").read_text(encoding="utf-8")

    assert "set_main_option" not in env


def test_dockerignore_excludes_local_tooling_without_excluding_admin_dist():
    entries = _active_dockerignore_entries()

    assert ".claude/" in entries
    assert ".superpowers/" in entries
    assert "static/" not in entries
    assert "static/admin-dist" not in entries
    assert "static/admin-dist/" not in entries
