# MySQL Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the backend run cleanly on MySQL and provide an Ubuntu runbook for moving existing PostgreSQL data into MySQL.

**Architecture:** Keep Python API/schema UUID values as `uuid.UUID`, but store them in MySQL-compatible `CHAR(36)` columns through a shared SQLAlchemy type. Update Alembic migrations to use the shared type so fresh MySQL deployments create the same schema the models expect.

**Tech Stack:** FastAPI, SQLAlchemy 2.x, Alembic, PyMySQL, pytest, pgloader on Ubuntu for one-time data migration.

---

### Task 1: Cross-Database UUID Type

**Files:**
- Create: `app/db_types.py`
- Modify: `app/models/family.py`
- Modify: `app/models/user.py`
- Modify: `app/models/task.py`
- Modify: `app/models/dictation_item.py`
- Modify: `app/models/submission.py`
- Modify: `app/models/mistake.py`
- Test: `tests/test_db_types.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_db_types.py` with a SQLite round-trip proving that a UUID can be inserted as `uuid.UUID`, queried back as `uuid.UUID`, and stored as a hyphenated string.

- [ ] **Step 2: Run the focused test**

Run: `.venv\Scripts\python.exe -m pytest tests/test_db_types.py -v`
Expected: FAIL because `app.db_types.GUID` does not exist.

- [ ] **Step 3: Implement `GUID`**

Create `app/db_types.py` with a SQLAlchemy `TypeDecorator` that uses PostgreSQL native UUID on PostgreSQL and `CHAR(36)` elsewhere.

- [ ] **Step 4: Wire models to `GUID`**

Set every UUID primary key and foreign key column to `mapped_column(GUID(), ...)`.

- [ ] **Step 5: Run the focused test**

Run: `.venv\Scripts\python.exe -m pytest tests/test_db_types.py -v`
Expected: PASS.

### Task 2: Alembic MySQL-Compatible Schema

**Files:**
- Modify: `alembic/versions/ab857114e5d3_create_users_and_families_tables.py`
- Modify: `alembic/versions/b8f589663c94_add_tasks_dictation_items_submissions_.py`
- Test: `tests/test_migrations_mysql.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_migrations_mysql.py` to assert migration files no longer contain `sa.Uuid()`.

- [ ] **Step 2: Run the focused test**

Run: `.venv\Scripts\python.exe -m pytest tests/test_migrations_mysql.py -v`
Expected: FAIL because current migrations use `sa.Uuid()`.

- [ ] **Step 3: Update migrations**

Import `GUID` from `app.db_types` and replace all `sa.Uuid()` columns with `GUID()`.

- [ ] **Step 4: Run the focused test**

Run: `.venv\Scripts\python.exe -m pytest tests/test_migrations_mysql.py -v`
Expected: PASS.

### Task 3: Ubuntu Migration Runbook

**Files:**
- Create: `docs/postgresql-to-mysql-migration.md`

- [ ] **Step 1: Document the production sequence**

Write concrete Ubuntu commands for backup, MySQL database creation, Alembic schema creation, `pgloader` import, validation queries, `.env` switch, and rollback notes.

- [ ] **Step 2: Include project-specific caveats**

Call out UUID storage as `CHAR(36)`, maintenance window/stop-write requirement, and table count verification for `families`, `users`, `tasks`, `dictation_items`, `submissions`, and `mistakes`.

### Task 4: Full Verification

**Files:**
- No production edits.

- [ ] **Step 1: Run backend tests**

Run: `.venv\Scripts\python.exe -m pytest tests/ -v`
Expected: PASS.

- [ ] **Step 2: Inspect git diff**

Run: `git diff -- app tests alembic docs`
Expected: Only MySQL compatibility and migration documentation changes.
