# API Tasks

- [x] **Task backend-007: 暴露计划创建、活动列表与详情 API**

**Files:**
- Create: `app/api/v1/homework_plans.py`, `tests/test_homework_plans_api.py`
- Modify: `app/main.py`

**Reasoning:** 先交付只读管理面与创建路径，验证路由注册、家长角色、家庭隔离及今日首次快照。

**Depends on:** backend-005

**Interfaces:**
- Consumes: create/get-active/get-detail CRUD, materializer, Create/Out schemas, `require_parent`.
- Produces: ledger POST/GET collection and GET detail endpoints.
- Contract checks: student 403; missing family 400; cross-family detail 404; template never appears in Task list.

**Step 1: Write the failing test**

```python
def test_parent_creates_plan_and_today_snapshot(client, parent_headers, today):
    response = client.post("/api/v1/homework-plans/", headers=parent_headers, json={
        "type": "home", "title": "每日阅读", "range_type": "week",
        "dictation_items": []})
    assert response.status_code == 200
    plan = response.json()
    assert plan["start_date"] == today.isoformat()
    tasks = client.get("/api/v1/tasks/", headers=parent_headers,
                       params={"task_date": today.isoformat()}).json()
    assert [t["source_plan_id"] for t in tasks] == [plan["id"]]
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_homework_plans_api.py::test_parent_creates_plan_and_today_snapshot -v`
Expected: FAIL with HTTP 404 because the router is not registered.

**Step 3: Write minimal implementation**

```python
router = APIRouter(prefix="/homework-plans", tags=["homework-plans"])
@router.post("/", response_model=HomeworkPlanDetailOut)
def create_homework_plan(body: HomeworkPlanCreate, user=Depends(require_parent), db=Depends(get_db)):
    _require_family(user)
    today = datetime.now(ZoneInfo(settings.BUSINESS_TIMEZONE)).date()
    plan = plan_crud.create_plan(db, user.family_id, user.id, body.resolve(today))
    if plan.start_date <= today:
        materialize_family_plans(SessionLocal, user.family_id, today)
    return plan_crud.get_plan_for_family(db, plan.id, user.family_id)
# Add parent-only active list/detail and register router in app/main.py.
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_homework_plans_api.py -k 'creates or lists or gets' -v`
Expected: PASS

**Step 5: Commit**

```bash
git add app/api/v1/homework_plans.py app/main.py tests/test_homework_plans_api.py
git commit -m "新增周期作业计划查询与创建接口"
```

- [x] **Task backend-008: 暴露完整更新与幂等软删除 API**

**Files:**
- Modify: `app/api/v1/homework_plans.py`, `tests/test_homework_plans_api.py`

**Reasoning:** 更新/删除共享锁定生命周期但有独立可观察错误语义；必须证明乐观冲突、开始日期锁定及快照隔离。

**Depends on:** backend-006, backend-007

**Interfaces:**
- Consumes: update/delete CRUD and HomeworkPlanUpdate.
- Produces: ledger PATCH and DELETE endpoints.
- Contract checks: stale token 409; invalid dates 422; cross-family 404; repeated DELETE succeeds; existing Task/words remain unchanged.

**Step 1: Write the failing test**

```python
def test_patch_conflict_and_snapshot_isolation(client, parent_headers, started_plan, snapshot):
    payload = full_update_payload(started_plan, title="新标题", updated_at="2000-01-01T00:00:00Z")
    stale = client.patch(f"/api/v1/homework-plans/{started_plan.id}",
                         headers=parent_headers, json=payload)
    assert stale.status_code == 409
    payload["updated_at"] = started_plan.updated_at.isoformat()
    ok = client.patch(f"/api/v1/homework-plans/{started_plan.id}",
                      headers=parent_headers, json=payload)
    assert ok.status_code == 200
    assert get_task(snapshot.id).title != "新标题"
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_homework_plans_api.py::test_patch_conflict_and_snapshot_isolation -v`
Expected: FAIL with HTTP 405 because PATCH is not defined.

**Step 3: Write minimal implementation**

```python
@router.patch("/{plan_id}", response_model=HomeworkPlanDetailOut)
def update_homework_plan(plan_id: UUID, body: HomeworkPlanUpdate,
                         user=Depends(require_parent), db=Depends(get_db)):
    _require_family(user)
    try:
        return plan_crud.update_plan(db, plan_id, user.family_id, body, business_today())
    except PlanVersionConflict:
        raise HTTPException(409, "Plan has changed")
@router.delete("/{plan_id}")
def delete_homework_plan(...):
    plan_crud.soft_delete_plan(db, plan_id, user.family_id)
    return {"ok": True}
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_homework_plans_api.py -k 'patch or delete' -v`
Expected: PASS

**Step 5: Commit**

```bash
git add app/api/v1/homework_plans.py tests/test_homework_plans_api.py
git commit -m "新增周期作业计划更新与删除接口"
```

- [x] **Task backend-009: 暴露显式同步并完成 Task 兼容回归**

**Files:**
- Modify: `app/api/v1/homework_plans.py`, `app/api/v1/tasks.py`, `tests/test_homework_plans_api.py`, `tests/test_tasks.py`

**Reasoning:** 最终集成点明确 POST 写、GET 纯读；同时验证学生可同步但不可管理、部分失败不阻塞已有作业展示。

**Depends on:** backend-006, backend-008

**Interfaces:**
- Consumes: materializer, business date, `get_current_user`, TaskOut optional source field.
- Produces: ledger POST materialize and GET Task compatibility behavior.
- Contract checks: partial failure HTTP 200/sanitized counts; both roles sync; GET before/after count unchanged without POST; all legacy tests pass.

**Step 1: Write the failing test**

```python
def test_get_tasks_never_materializes(client, student_headers, active_plan, db):
    before = db.query(Task).filter(Task.source_plan_id == active_plan.id).count()
    assert client.get("/api/v1/tasks/", headers=student_headers).status_code == 200
    db.expire_all()
    assert db.query(Task).filter(Task.source_plan_id == active_plan.id).count() == before
    sync = client.post("/api/v1/homework-plans/materialize", headers=student_headers)
    assert sync.status_code == 200
    assert sync.json()["created_count"] > 0
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_homework_plans_api.py::test_get_tasks_never_materializes -v`
Expected: FAIL with HTTP 405/404 for missing materialize endpoint.

**Step 3: Write minimal implementation**

```python
@router.post("/materialize", response_model=MaterializeResult)
def materialize_plans(user=Depends(get_current_user)):
    _require_family(user)
    return materialize_family_plans(SessionLocal, user.family_id, business_today())

def _to_task_out(task):
    return TaskOut(..., source_plan_id=task.source_plan_id,
                   has_dictation=bool(task.dictation_items))
# Do not invoke materializer from list_tasks. Add partial-failure monkeypatch test asserting
# 200, failed_count, stable error_code, then GET still returns previously committed tasks.
```

**Step 4: Run test to verify it passes**

Run: `rm -f test.db && python -m pytest tests/ -v`
Expected: PASS

**Step 5: Commit**

```bash
git add app/api/v1/homework_plans.py app/api/v1/tasks.py tests/test_homework_plans_api.py tests/test_tasks.py
git commit -m "完成周期作业同步与兼容性验证"
```
