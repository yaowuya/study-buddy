from pathlib import Path


def test_alembic_migrations_do_not_use_generic_uuid_type():
    versions_dir = Path("alembic/versions")
    offenders = []

    for migration in versions_dir.glob("*.py"):
        content = migration.read_text(encoding="utf-8")
        if "sa.Uuid()" in content:
            offenders.append(migration.name)

    assert offenders == []
