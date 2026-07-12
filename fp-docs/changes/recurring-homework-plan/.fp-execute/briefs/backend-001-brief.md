# Task Brief: backend-001

## Identity

- Change slug: `recurring-homework-plan`
- Task owner file: `fp-docs/changes/recurring-homework-plan/tasks/backend/10-domain-tasks.md`
- Resolved plan context: `tasks/00-overview.md`; backend split manifest `tasks/backend/00-index.md` in listed order; frontend split manifest present for cross-end graph.
- Task heading: `Task backend-001: 建立计划领域模型与 Task 来源约束`
- Task checkbox line: `- [ ] **Task backend-001: 建立计划领域模型与 Task 来源约束**`
- Declared dependencies: None
- Controller base SHA: `f5c744b7db6ceb44070fbf6691479483a70480e1`

## Resolved Artifact Contract

| Logical artifact | Canonical entry | Resolution mode | Ordered fragments |
| --- | --- | --- | --- |
| PRD | `prd.md` | small | N/A |
| Proposal | `proposal.md` | small | N/A |
| Backend design | `design/backend/00-index.md` | split | `01-domain-and-api.md`, `02-materialization-and-consistency.md` |
| Frontend design | `design/frontend/00-index.md` | split | `01-data-flow-and-pages.md`, `02-components-and-visual-contract.md` |
| Backend plan | `tasks/backend/00-index.md` | split | `01-context.md`, `05-interfaces.md`, `10-domain-tasks.md`, `20-materialization-tasks.md`, `30-api-tasks.md`, `90-coverage.md` |
| Frontend plan | `tasks/frontend/00-index.md` | split | `01-context.md`, `05-interfaces.md`, `10-foundation-tasks.md`, `20-creation-tasks.md`, `30-dashboard-tasks.md`, `40-editing-tasks.md`, `90-coverage.md` |

- Structural conflict: None.
- Task ownership proof: backend manifest Kind=`tasks` row for `10-domain-tasks.md`; unique ID/checkbox verified.
- Overview applicability: two-end `tasks/00-overview.md`, 0/19 complete before dispatch.
- Structural validation: manifests complete; dependencies acyclic; no forbidden checkbox or hard-limit violation.

## Status

- Ledger status before dispatch: `not-started`
- Prior attempts: none

## Applicable Global Constraints

- FastAPI/Pydantic v2/SQLAlchemy 2.x/Alembic/pytest; no new dependency.
- UUID primary keys and existing `GUID` type.
- Existing Task semantics and old rows remain compatible.
- `BUSINESS_TIMEZONE="Asia/Shanghai"` and `MAX_HOMEWORK_PLAN_DAYS=366` are explicitly user-confirmed.
- `UNIQUE(source_plan_id, date)` excludes `is_deleted`.
- Plan template item cascade must not cascade generated Tasks.
- Chinese commit message.

## Relevant Project Information Layer

- FeaturePilot manifest: absent; compatibility execution approved and recorded.
- Current-code facts: `app/models/task.py`, `app/models/dictation_item.py`, `app/models/__init__.py`, `app/core/config.py` must be read before editing.
- Unknowns checked: timezone and maximum range resolved by user.
- Staleness notes: generated docs guide scope; current source is final implementation fact.

## Proposal / Design Context

> 新增独立作业计划领域模型；作业实例记录来源计划，以数据库唯一约束保证幂等。

> `HomeworkPlan` owns mutable template fields and ordered template dictation items. `Task.source_plan_id` is nullable, retains source after soft deletion, and `(source_plan_id,date)` is unique.

## Prior Interfaces Available

| Interface | Source | Contract | Evidence |
| --- | --- | --- | --- |
| `Base`, `GUID` | existing code | SQLAlchemy base and cross-dialect UUID | `app/database.py`, `app/db_types.py` |
| `TaskType`, `Task` | existing code | school/home and concrete task model | `app/models/task.py` |
| `Settings` | existing code | Pydantic settings | `app/core/config.py` |

## Full Task Text

```text
Task backend-001: 建立计划领域模型与 Task 来源约束
Files: Create app/models/homework_plan.py; modify app/models/task.py, app/models/__init__.py, app/core/config.py; test tests/test_homework_plan_models.py.
Reasoning: 数据库模型和业务时区是全部计划行为的最小基础；唯一键必须先于幂等服务存在。
Depends on: None.
Interfaces: consume Base/GUID/TaskType/Task/DictationItem relationships; produce Settings fields, HomeworkPlan, HomeworkPlanDictationItem, Task.source_plan_id; check FKs/indexes/template-only cascade/unique source-plan-date.
Red: add test constructing plan, asserting default false, Asia/Shanghai config, unique constraint name, nullable source field. Run `python -m pytest tests/test_homework_plan_models.py::test_plan_models_and_task_source_constraints -v`; expected ModuleNotFoundError.
Minimal implementation: exact design fields, ordered HomeworkPlanDictationItem, nullable Task source FK and relationship, `UniqueConstraint("source_plan_id", "date", name="uq_tasks_source_plan_date")`; config timezone and max days.
Green: `python -m pytest tests/test_homework_plan_models.py -v`.
Commit: `git add app/core/config.py app/models tests/test_homework_plan_models.py && git commit -m "新增周期作业计划领域模型"`.
```

## Allowed Scope

The implementer may edit only:
- `app/models/homework_plan.py`
- `app/models/task.py`
- `app/models/__init__.py`
- `app/core/config.py`
- `tests/test_homework_plan_models.py`
- `.fp-execute/reports/backend-001-report.md`

The implementer must not edit neighboring tasks, migrations, schemas, proposal/design/plan files, or unrelated code.

## Required Evidence

- Failing command and key failure.
- Passing model test output.
- Metadata interface/constraint evidence.
- Commit SHA.
- Report path and concerns.
