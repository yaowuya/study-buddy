# Domain and Contract Tasks

- [x] **Task backend-001: 建立计划领域模型与 Task 来源约束**

**Files:**
- Create: `app/models/homework_plan.py`
- Modify: `app/models/task.py`, `app/models/__init__.py`, `app/core/config.py`
- Test: `tests/test_homework_plan_models.py`

**Reasoning:** 数据库模型和业务时区是全部计划行为的最小基础；唯一键必须先于幂等服务存在。

**Depends on:** None

**Interfaces:**
- Consumes: existing `Base`, `GUID`, `TaskType`, `Task`, `DictationItem` relationships.
- Produces: ledger `Settings` fields, `HomeworkPlan`, `HomeworkPlanDictationItem`, `Task.source_plan_id`.
- Contract checks: metadata contains FKs, indexes, cascade only for template items, and unique `(source_plan_id,date)`.

**Step 1: Write the failing test**

```python
def test_plan_models_and_task_source_constraints(db):
    plan = HomeworkPlan(family_id=uuid4(), created_by=uuid4(), type=TaskType.HOME,
        title="每日听写", start_date=date(2026, 7, 11), end_date=date(2026, 7, 17))
    assert plan.is_deleted is False
    assert settings.BUSINESS_TIMEZONE == "Asia/Shanghai"
    names = {c.name for c in Task.__table__.constraints}
    assert "uq_tasks_source_plan_date" in names
    assert Task.__table__.c.source_plan_id.nullable
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_homework_plan_models.py::test_plan_models_and_task_source_constraints -v`
Expected: FAIL with `ModuleNotFoundError: app.models.homework_plan`.

**Step 3: Write minimal implementation**

```python
class HomeworkPlan(Base):
    __tablename__ = "homework_plans"
    id: Mapped[UUID] = mapped_column(GUID(), primary_key=True, default=uuid4)
    family_id: Mapped[UUID] = mapped_column(GUID(), ForeignKey("families.id"), index=True)
    created_by: Mapped[UUID] = mapped_column(GUID(), ForeignKey("users.id"))
    type: Mapped[TaskType] = mapped_column(String(10))
    title: Mapped[str] = mapped_column(String(100))
    desc: Mapped[str | None] = mapped_column(Text)
    duration: Mapped[int | None] = mapped_column(Integer)
    subject: Mapped[str | None] = mapped_column(String(20))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
# Add ordered HomeworkPlanDictationItem and Task source_plan_id relationship;
# set __table_args__=(UniqueConstraint("source_plan_id", "date", name="uq_tasks_source_plan_date"),).
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_homework_plan_models.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add app/core/config.py app/models tests/test_homework_plan_models.py
git commit -m "新增周期作业计划领域模型"
```

- [x] **Task backend-002: 添加存量安全数据库迁移**

**Files:**
- Create: `alembic/versions/<revision>_add_homework_plans.py`
- Modify: `tests/test_homework_plan_models.py`

**Reasoning:** 部署必须先建立模板表和可空来源字段，且旧 Task 行保持 NULL；迁移可独立审查和回滚。

**Depends on:** backend-001

**Interfaces:**
- Consumes: ledger model/table contract.
- Produces: Alembic upgrade/downgrade schema matching ORM metadata.
- Contract checks: upgrade over a pre-feature task row retains it and accepts multiple NULL sources.

**Step 1: Write the failing test**

```python
def test_migration_upgrade_preserves_existing_tasks(alembic_runner):
    alembic_runner.migrate_before("add_homework_plans")
    old_id = alembic_runner.insert_legacy_task(title="旧作业")
    alembic_runner.upgrade_head()
    row = alembic_runner.fetch_task(old_id)
    assert row["source_plan_id"] is None
    assert {"homework_plans", "homework_plan_dictation_items"} <= alembic_runner.tables()
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_homework_plan_models.py::test_migration_upgrade_preserves_existing_tasks -v`
Expected: FAIL because revision/table `add_homework_plans` does not exist.

**Step 3: Write minimal implementation**

```python
def upgrade():
    op.create_table("homework_plans", ...)
    op.create_table("homework_plan_dictation_items", ...)
    op.add_column("tasks", sa.Column("source_plan_id", GUID(), nullable=True))
    op.create_foreign_key("fk_tasks_source_plan", "tasks", "homework_plans", ["source_plan_id"], ["id"])
    op.create_unique_constraint("uq_tasks_source_plan_date", "tasks", ["source_plan_id", "date"])
# Add family/range and plan-item indexes; downgrade removes them in reverse dependency order.
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_homework_plan_models.py tests/test_migrations_mysql.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add alembic/versions tests/test_homework_plan_models.py
git commit -m "添加周期作业计划数据库迁移"
```

- [x] **Task backend-003: 定义计划与同步 Schema 契约**

**Files:**
- Create: `app/schemas/homework_plan.py`, `tests/test_homework_plan_schemas.py`
- Modify: `app/schemas/task.py`

**Reasoning:** 在 CRUD/API 前冻结范围计算、完整更新、词条规范化和响应形状，避免后续临时发明字段。

**Depends on:** backend-001

**Interfaces:**
- Consumes: TaskType, configured timezone/day limit, existing `DictationItemCreate`.
- Produces: ledger Create/Update/Out/DetailOut/Materialize result schemas and optional `TaskOut.source_plan_id`.
- Contract checks: presets ignore supplied dates; custom/date/duration/items/token constraints emit 422-compatible validation errors.

**Step 1: Write the failing test**

```python
def test_create_ranges_and_dictation_validation(monkeypatch):
    today = date(2026, 7, 11)
    week = HomeworkPlanCreate(type="home", title="练习", range_type="week",
                              start_date=date(2000, 1, 1), end_date=date(2000, 1, 2))
    assert week.resolve_dates(today) == (today, date(2026, 7, 17))
    with pytest.raises(ValidationError):
        HomeworkPlanCreate(type="home", title="听写", range_type="custom",
            start_date=today, end_date=today, dictation_items=[{"content":"词"}, {"content":" 词 "}])
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_homework_plan_schemas.py::test_create_ranges_and_dictation_validation -v`
Expected: FAIL with `ModuleNotFoundError: app.schemas.homework_plan`.

**Step 3: Write minimal implementation**

```python
class HomeworkPlanCreate(BaseModel):
    type: TaskType; title: str; desc: str | None = None; duration: int | None = None
    subject: str | None = None; range_type: Literal["week", "month", "custom"]
    start_date: date | None = None; end_date: date | None = None
    dictation_items: list[DictationItemCreate] = []
    def resolve_dates(self, today: date) -> tuple[date, date]:
        if self.range_type in ("week", "month"):
            return today, today + timedelta(days=6 if self.range_type == "week" else 29)
        assert self.start_date is not None and self.end_date is not None
        return self.start_date, self.end_date
# Add model validators and all ledger output/result models; TaskOut.source_plan_id defaults None.
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_homework_plan_schemas.py tests/test_tasks.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add app/schemas tests/test_homework_plan_schemas.py tests/test_tasks.py
git commit -m "定义周期作业计划接口契约"
```
