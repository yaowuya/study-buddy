from __future__ import annotations

import argparse
import uuid
from collections.abc import Sequence
from typing import Any

from sqlalchemy import MetaData, Table, create_engine, inspect, select, text
from sqlalchemy.engine import Engine


DEFAULT_TABLES = [
    "families",
    "users",
    "tasks",
    "dictation_items",
    "submissions",
    "mistakes",
]


def create_database_engine(url: str) -> Engine:
    return create_engine(url)


def count_rows(engine: Engine, table_name: str) -> int:
    with engine.connect() as connection:
        result = connection.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        return int(result.scalar_one())


def table_columns(engine: Engine, table_name: str) -> list[str]:
    inspector = inspect(engine)
    return [column["name"] for column in inspector.get_columns(table_name)]


def normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        key: str(value) if isinstance(value, uuid.UUID) else value
        for key, value in row.items()
    }


def fetch_rows(engine: Engine, table_name: str, columns: Sequence[str]) -> list[dict[str, Any]]:
    metadata = MetaData()
    table = Table(table_name, metadata, autoload_with=engine)
    selected_columns = [table.c[column] for column in columns]

    with engine.connect() as connection:
        result = connection.execute(select(*selected_columns))
        return [normalize_row(dict(row)) for row in result.mappings()]


def delete_target_rows(engine: Engine, tables: Sequence[str]) -> None:
    with engine.begin() as connection:
        for table_name in reversed(tables):
            connection.execute(text(f"DELETE FROM {table_name}"))


def insert_rows(engine: Engine, table_name: str, rows: Sequence[dict[str, Any]]) -> None:
    if not rows:
        return

    metadata = MetaData()
    table = Table(table_name, metadata, autoload_with=engine)
    with engine.begin() as connection:
        connection.execute(table.insert(), list(rows))


def migrate_database(
    source_url: str,
    target_url: str,
    tables: Sequence[str] | None = None,
    truncate: bool = True,
    dry_run: bool = False,
) -> dict[str, int]:
    table_names = list(tables or DEFAULT_TABLES)
    source_engine = create_database_engine(source_url)
    target_engine = create_database_engine(target_url)

    row_counts = {table_name: count_rows(source_engine, table_name) for table_name in table_names}
    if dry_run:
        return row_counts

    if truncate:
        delete_target_rows(target_engine, table_names)

    for table_name in table_names:
        columns = table_columns(target_engine, table_name)
        rows = fetch_rows(source_engine, table_name, columns)
        insert_rows(target_engine, table_name, rows)

    return row_counts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Copy Study Buddy data from PostgreSQL to an Alembic-created MySQL schema.",
    )
    parser.add_argument("--source", required=True, help="Source PostgreSQL SQLAlchemy URL.")
    parser.add_argument("--target", required=True, help="Target MySQL SQLAlchemy URL.")
    parser.add_argument(
        "--tables",
        nargs="+",
        default=DEFAULT_TABLES,
        help="Tables to migrate in dependency order.",
    )
    parser.add_argument(
        "--no-truncate",
        action="store_true",
        help="Do not delete existing rows in target tables before inserting.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only print source row counts without writing to the target.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    row_counts = migrate_database(
        source_url=args.source,
        target_url=args.target,
        tables=args.tables,
        truncate=not args.no_truncate,
        dry_run=args.dry_run,
    )

    action = "Would migrate" if args.dry_run else "Migrated"
    for table_name, row_count in row_counts.items():
        print(f"{action} {row_count} rows from {table_name}")


if __name__ == "__main__":
    main()
