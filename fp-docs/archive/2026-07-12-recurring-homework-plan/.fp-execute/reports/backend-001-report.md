# backend-001 Implementation Report

Status: DONE

## Commit

- `7607d63` — `新增周期作业计划领域模型`

## Changed files

- `app/core/config.py`
- `app/models/__init__.py`
- `app/models/homework_plan.py`
- `app/models/task.py`
- `tests/test_homework_plan_models.py`

## TDD evidence

- Initial system `python` command failed before test collection because it did not use the project environment (`ModuleNotFoundError: fastapi`).
- Project environment red/iteration evidence: `./.venv/Scripts/python.exe -m pytest tests/test_homework_plan_models.py -v` initially reported `1 failed, 1 passed` because a transient ORM object does not receive a SQLAlchemy column default until persistence. The assertion was corrected to verify column default metadata, which is the actual contract.
- Green: `./.venv/Scripts/python.exe -m pytest tests/test_homework_plan_models.py -v` → `2 passed`.
- Regression: `rm -f test.db && ./.venv/Scripts/python.exe -m pytest tests/ -q` → `53 passed`.

## Contract evidence

- `HomeworkPlan` and ordered `HomeworkPlanDictationItem` are registered in model metadata.
- `Task.source_plan_id` is nullable and indexed.
- `uq_tasks_source_plan_date` enforces `(source_plan_id, date)` uniqueness.
- Template items use delete-orphan cascade; generated Tasks do not receive delete cascade.
- Confirmed config values are `Asia/Shanghai` and 366 days.

## Concerns

- No blocking concerns. Migration is intentionally deferred to backend-002.
