# Materialization Tasks

- [x] **Task backend-004: 实现家庭范围计划生命周期与活动聚合**

**Files:**
- Create: `app/crud/homework_plan.py`, `tests/test_homework_plan_crud.py`

**Reasoning:** 生命周期和活动卡派生数据属于同一持久化边界；家庭过滤、锁和聚合必须在 API 之前可独立验证。

**Depends on:** backend-002, backend-003

**Interfaces:**
- Consumes: plan models and Create/Update schemas.
- Produces: ledger `create_plan`, `get_active_plans`, `get_plan_for_family`, `update_plan`, `soft_delete_plan`.
- Contract checks: family isolation is present in every query; one aggregate query supplies generated counts; mutations lock before revalidation.

**Step 1: Write the failing test**

```python
def test_active_plans_are_family_scoped_and_aggregated(db, families, parents):
    mine = create_plan(db, families.a.id, parents.a.id, plan_command(end_date=date.today()))
    create_plan(db, families.b.id, parents.b.id, plan_command(end_date=date.today()))
    db.add_all([Task(family_id=families.a.id, source_plan_id=mine.id, date=date.today(),
                     type="home", title="快照")])
    rows = get_active_plans(db, families.a.id, date.today())
    assert [(row.plan.id, row.generated_count) for row in rows] == [(mine.id, 1)]
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_homework_plan_crud.py::test_active_plans_are_family_scoped_and_aggregated -v`
Expected: FAIL with `ModuleNotFoundError: app.crud.homework_plan`.

**Step 3: Write minimal implementation**

```python
def get_active_plans(db, family_id, today):
    generated = (db.query(Task.source_plan_id.label("plan_id"), func.count(Task.id).label("count"))
        .filter(Task.source_plan_id.is_not(None)).group_by(Task.source_plan_id).subquery())
    return (db.query(HomeworkPlan, func.coalesce(generated.c.count, 0))
        .outerjoin(generated, generated.c.plan_id == HomeworkPlan.id)
        .filter(HomeworkPlan.family_id == family_id, HomeworkPlan.is_deleted.is_(False),
                HomeworkPlan.end_date >= today).all())
# create_plan normalizes ordered items; update/delete select plan with with_for_update(),
# compare updated_at and preserve tasks; delete is idempotent.
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_homework_plan_crud.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add app/crud/homework_plan.py tests/test_homework_plan_crud.py
git commit -m "实现周期作业计划生命周期"
```

- [ ] **Task backend-005: 实现遗漏日期与快照物化服务**

**Files:**
- Create: `app/services/__init__.py`, `app/services/homework_plan_materializer.py`, `tests/test_homework_plan_materializer.py`

**Reasoning:** 补生成是独立业务服务：必须覆盖过期但有遗漏的计划、集合差、听写快照和逐计划失败隔离，而不耦合 Task 查询。

**Depends on:** backend-002, backend-003, backend-004

**Interfaces:**
- Consumes: candidate plan/model locks, Task/DictationItem, result schemas.
- Produces: ledger `date_range` and `materialize_family_plans`.
- Contract checks: inclusive leap/cross-boundary ranges, one existing-date query, ascending snapshots, per-plan atomic rollback and sanitized errors.

**Step 1: Write the failing test**

```python
def test_backfills_missing_dates_idempotently(session_factory, plan_with_words):
    first = materialize_family_plans(session_factory, plan_with_words.family_id, date(2026, 7, 13))
    second = materialize_family_plans(session_factory, plan_with_words.family_id, date(2026, 7, 13))
    assert first.created_count == 3
    assert second.created_count == 0
    with session_factory() as db:
        tasks = db.query(Task).filter(Task.source_plan_id == plan_with_words.id).order_by(Task.date).all()
        assert [t.date for t in tasks] == [date(2026, 7, 11), date(2026, 7, 12), date(2026, 7, 13)]
        assert [[i.content for i in t.dictation_items] for t in tasks] == [["甲", "乙"]] * 3
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_homework_plan_materializer.py::test_backfills_missing_dates_idempotently -v`
Expected: FAIL with `ModuleNotFoundError: app.services.homework_plan_materializer`.

**Step 3: Write minimal implementation**

```python
def date_range(start, end):
    return [] if end < start else [start + timedelta(days=n) for n in range((end-start).days + 1)]

def materialize_family_plans(session_factory, family_id, through_date):
    plan_ids = _candidate_plan_ids(session_factory, family_id, through_date)  # includes expired plans
    results = []
    for plan_id in plan_ids:
        try:
            with session_factory.begin() as db:
                plan = _lock_and_revalidate(db, plan_id, family_id, through_date)
                created = _create_missing_snapshots(db, plan, through_date)
            results.append(PlanMaterializeResult.success(plan_id, created))
        except Exception:
            logger.exception("plan materialization failed", extra={"plan_id": str(plan_id)})
            results.append(PlanMaterializeResult.failed(plan_id, "materialization_failed"))
    return MaterializeResult.from_plans(results)
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_homework_plan_materializer.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add app/services tests/test_homework_plan_materializer.py
git commit -m "实现周期作业遗漏补生成"
```

- [ ] **Task backend-006: 验证并发锁、幂等冲突和编辑删除竞争**

**Files:**
- Modify: `app/crud/homework_plan.py`, `app/services/homework_plan_materializer.py`
- Create: `tests/test_homework_plan_concurrency.py`

**Reasoning:** SQLite 无法证明行锁；真实 PostgreSQL 双 Session 测试独立验证统一锁顺序和唯一冲突最终防线。

**Depends on:** backend-005

**Interfaces:**
- Consumes: lifecycle mutations and materializer.
- Produces: ledger plan-lock protocol and same-key IntegrityError classification.
- Contract checks: concurrent materialize yields one row/date; edit/delete wait then new transaction sees committed template/deletion.

**Step 1: Write the failing test**

```python
@pytest.mark.skipif(not os.getenv("TEST_POSTGRES_URL"), reason="requires TEST_POSTGRES_URL")
def test_concurrent_materialize_creates_one_task_per_date(pg_session_factory, pg_plan, barrier):
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: materialize_family_plans(
            pg_session_factory, pg_plan.family_id, pg_plan.start_date), range(2)))
    with pg_session_factory() as db:
        assert db.query(Task).filter(Task.source_plan_id == pg_plan.id,
                                     Task.date == pg_plan.start_date).count() == 1
    assert sum(r.created_count for r in results) == 1
```

**Step 2: Run test to verify it fails**

Run: `TEST_POSTGRES_URL="$DATABASE_URL" python -m pytest tests/test_homework_plan_concurrency.py::test_concurrent_materialize_creates_one_task_per_date -v`
Expected: FAIL with duplicate/lock assertion because all write paths do not yet use the finalized lock/conflict protocol.

**Step 3: Write minimal implementation**

```python
def _lock_plan(db, plan_id):
    return db.query(HomeworkPlan).filter(HomeworkPlan.id == plan_id).with_for_update().one_or_none()

def _is_same_materialization_key(db, plan_id, target_date):
    return db.query(Task.id).filter(Task.source_plan_id == plan_id, Task.date == target_date).first() is not None
# Use _lock_plan before update/delete/generate revalidation. On IntegrityError rollback the
# plan transaction, then only classify idempotent when every conflicted (plan_id,date) exists;
# otherwise return materialization_failed. Add edit/materialize and delete/materialize tests.
```

**Step 4: Run test to verify it passes**

Run: `TEST_POSTGRES_URL="$DATABASE_URL" python -m pytest tests/test_homework_plan_concurrency.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add app/crud/homework_plan.py app/services/homework_plan_materializer.py tests/test_homework_plan_concurrency.py
git commit -m "完善周期作业并发一致性"
```
