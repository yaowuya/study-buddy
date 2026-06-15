from pathlib import Path


def test_entrypoint_has_stdout_fallback_when_log_dir_is_not_writable():
    script = Path("docker-entrypoint.sh").read_text(encoding="utf-8")

    assert "-w \"$LOG_DIR\"" in script
    assert "--access-logfile -" in script
    assert "--error-logfile -" in script


def test_migration_doc_mentions_docker_database_url_encoding():
    doc = Path("docs/postgresql-to-mysql-migration.md").read_text(encoding="utf-8")

    assert "host.docker.internal" in doc
    assert "%40" in doc


def test_alembic_env_does_not_write_database_url_through_configparser():
    env = Path("alembic/env.py").read_text(encoding="utf-8")

    assert "set_main_option" not in env
