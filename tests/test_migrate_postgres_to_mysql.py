import sqlite3
import uuid

from sqlalchemy import create_engine, text

from scripts.migrate_postgres_to_mysql import DEFAULT_TABLES, migrate_database, normalize_row


def _create_source_database(path):
    connection = sqlite3.connect(path)
    connection.executescript(
        """
        CREATE TABLE families (
            id TEXT PRIMARY KEY,
            code TEXT NOT NULL
        );
        CREATE TABLE users (
            id TEXT PRIMARY KEY,
            phone TEXT NOT NULL,
            family_id TEXT
        );
        INSERT INTO families (id, code) VALUES ('family-1', 'ABC123');
        INSERT INTO users (id, phone, family_id)
        VALUES ('user-1', '13800000000', 'family-1');
        """
    )
    connection.commit()
    connection.close()


def _create_target_database(path):
    connection = sqlite3.connect(path)
    connection.executescript(
        """
        CREATE TABLE families (
            id TEXT PRIMARY KEY,
            code TEXT NOT NULL
        );
        CREATE TABLE users (
            id TEXT PRIMARY KEY,
            phone TEXT NOT NULL,
            family_id TEXT
        );
        INSERT INTO families (id, code) VALUES ('old-family', 'OLD001');
        """
    )
    connection.commit()
    connection.close()


def test_default_table_order_keeps_parent_tables_before_children():
    assert DEFAULT_TABLES == [
        "families",
        "users",
        "tasks",
        "dictation_items",
        "submissions",
        "mistakes",
    ]


def test_migrate_database_copies_rows_and_truncates_target_first(tmp_path):
    source_path = tmp_path / "source.db"
    target_path = tmp_path / "target.db"
    _create_source_database(source_path)
    _create_target_database(target_path)

    result = migrate_database(
        f"sqlite:///{source_path}",
        f"sqlite:///{target_path}",
        tables=["families", "users"],
        truncate=True,
        dry_run=False,
    )

    assert result == {"families": 1, "users": 1}

    engine = create_engine(f"sqlite:///{target_path}")
    with engine.connect() as connection:
        families = connection.execute(text("SELECT id, code FROM families")).all()
        users = connection.execute(text("SELECT id, phone, family_id FROM users")).all()

    assert families == [("family-1", "ABC123")]
    assert users == [("user-1", "13800000000", "family-1")]


def test_dry_run_counts_rows_without_changing_target(tmp_path):
    source_path = tmp_path / "source.db"
    target_path = tmp_path / "target.db"
    _create_source_database(source_path)
    _create_target_database(target_path)

    result = migrate_database(
        f"sqlite:///{source_path}",
        f"sqlite:///{target_path}",
        tables=["families", "users"],
        truncate=True,
        dry_run=True,
    )

    assert result == {"families": 1, "users": 1}

    engine = create_engine(f"sqlite:///{target_path}")
    with engine.connect() as connection:
        families = connection.execute(text("SELECT id, code FROM families")).all()

    assert families == [("old-family", "OLD001")]


def test_normalize_row_converts_uuid_values_to_strings():
    value = uuid.uuid4()

    assert normalize_row({"id": value, "code": "ABC123"}) == {
        "id": str(value),
        "code": "ABC123",
    }
